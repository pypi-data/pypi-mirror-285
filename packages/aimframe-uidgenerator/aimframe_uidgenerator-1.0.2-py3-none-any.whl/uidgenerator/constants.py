class Constants:

    # 类似于 C# 中的 const，Python 中使用类属性来定义常量
    UidGeneratorLoggerName = "AimFrame.UIdGenerator"
    MaxDataCenterWorkIdBits = 10
    DataCenterIdBits = 5
    WorkerIdBits = MaxDataCenterWorkIdBits - DataCenterIdBits

    MaxWorkerId = -1 ^ (-1 << WorkerIdBits)
    MaxDataCenterIdId = -1 ^ (-1 << DataCenterIdBits)
    SequenceBits = 12

    WorkerIdShift = SequenceBits
    MaxDataCenterIdIdShift = SequenceBits + WorkerIdBits

    TwePoch = 1288834974657

    TimeStampLeftShiftLeftShift = SequenceBits + WorkerIdBits + DataCenterIdBits
    SequenceMask = -1 ^ (-1 << SequenceBits)
    MAX_BACKWARD_MS = 3
