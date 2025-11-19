from zk import ZK, const

device_ip = "192.168.10.207"
device_port = 8085
device_password = 000000   # keep integer or string

zk = ZK(
    device_ip,
    port=device_port,
    timeout=10,
    password=device_password,
    force_udp=False,
    ommit_ping=False
)

try:
    print("Connecting...")
    conn = zk.connect()
    print("Connected Successfully!")

    # Get device info
    print("Device Info:")
    print("  Firmware:", conn.get_firmware_version())
    print("  Platform:", conn.get_platform())
    print("  Serial Number:", conn.get_serialnumber())

    # Read attendance logs
    print("\nDownloading Attendance Logs...")
    records = conn.get_attendance()
    for r in records:
        print(r)

    # Example: clear attendance
    # conn.clear_attendance()

    # Disconnect
    conn.disconnect()
    print("Disconnected!")

except Exception as e:
    print("Connection failed:", e)
