from zk import ZK, const

conn = None
zk = ZK('192.168.0.116', port=4370, timeout=5, password=0) # password 0 = empty password

try:
    print("ডিভাইসের সাথে সংযোগ স্থাপনের চেষ্টা করা হচ্ছে...")
    conn = zk.connect()
    print("সফলভাবে সংযুক্ত হয়েছে!")
    # এখানে আপনি ইউজার লিস্ট, অ্যাটেনডেন্স ইত্যাদি আনতে পারেন
    # users = conn.get_users()
    # attendance = conn.get_attendance()
    # print(attendance)
except Exception as e:
    print(f"প্রসেসিং এ সমস্যা হয়েছে: {e}")
finally:
    if conn:
        conn.disconnect()
        print("সংযোগ বিচ্ছিন্ন হয়েছে।")