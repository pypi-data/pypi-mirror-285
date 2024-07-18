from enum import Enum

class EventStatus(Enum):

    Checked_out = 2
    Complete = 4
    Error = 5
    Pending = 1
    Processing = 3
    Timed_out = 6


class EventType:

    class Video(Enum):
        Start_bars = 9
        Follow = 8
        Receive_stream = 5
        Start_recording = 1
        Start_streaming = 3
        Stop_bars = 10
        Stop_receive_stream = 6
        Stop_recording = 2
        Stop_streaming = 4
        Test_event = 7
        Test_stop = 11

    class Transcoding(Enum):  
        Transcode_file = 12
        Concatenate_files = 16

    class Transfer(Enum):  
        Transfer_file = 13


class Event:

    def __init__(self, key: int, userID: int, deviceID: int, agentTypeID: int, agentID: int, eventTypeID: int, eventStatus: str, eventParameters: str, processID: int, result: str, percentComplete: int, priority: int, expirationEpoch: int, attemptNumber: int, maxAttempts: int, checkoutToken: str, tagString: str, tagNumber: int, creationDate: str, createdBy: int, lastModifiedDate: str, lastModifiedBy: int):

        self.eventID = key
        self.userID = userID
        self.deviceID = deviceID
        self.agentTypeID = agentTypeID
        self.agentID = agentID
        self.eventTypeID = eventTypeID
        self.eventStatus = eventStatus
        self.eventParameters = eventParameters
        self.processID = processID
        self.result = result
        self.percentComplete = percentComplete
        self.priority = priority
        self.expirationEpoch = expirationEpoch
        self.attemptNumber = attemptNumber
        self.maxAttempts = maxAttempts
        self.checkoutToken = checkoutToken
        self.tagString = tagString
        self.tagNumber = tagNumber
        self.creationDate = creationDate
        self.createdBy = createdBy
        self.lastModifiedDate = lastModifiedDate
        self.lastModifiedBy = lastModifiedBy


class EventWithNames(Event):

    def __init__(self, key: int, userID: int, deviceID: int, agentTypeID: int, agentID: int, eventTypeID: int, eventStatus: str, eventParameters: str, processID: int, result: str, percentComplete: int, priority: int, expirationEpoch: int, attemptNumber: int, maxAttempts: int, checkoutToken: str, tagString: str, tagNumber: int, creationDate: str, createdBy: int, lastModifiedDate: str, lastModifiedBy: int, deviceName: str, eventType: str, agentType: str, version: str, eventStatusName: str, agentIndex: int):
        super().__init__(key, userID, deviceID, agentTypeID, agentID, eventTypeID, eventStatus, eventParameters, processID, result, percentComplete, priority, expirationEpoch, attemptNumber, maxAttempts, checkoutToken, tagString, tagNumber, creationDate, createdBy, lastModifiedDate, lastModifiedBy)
        self.deviceName = deviceName
        self.eventType = eventType
        self.agentType = agentType
        self.version = version
        self.eventStatusName = eventStatusName
        self.agentIndex = agentIndex


class RecordingParameters:

    def __init__(self, height: int = 1920, width: int = 1080, fps: float = 30, bitrate: int = 5000000, vflip: int = 0, hflip: int = 0, encoding: str = '', segmentLengthSeconds: float = 0, audio: int = 0):
        self.height = height
        self.width = width
        self.fps = fps
        self.bitrate = bitrate
        self.vflip = vflip
        self.hflip = hflip
        self.encoding = encoding
        self.segmentLengthSeconds = segmentLengthSeconds
        self.audio = audio


class File:

    def __init__(self, key = 0, userID = 0, deviceID = 0, filename = '', fileGUID = '', sHA256Hash = '', fileLocation = '', fileExpiration = '', fileSize = '', fileInS3 = False, creationDate = '', createdBy = '', lastModifiedDate = '', lastModifiedBy = 0):
        self.key = key
        self.userID = userID
        self.deviceID = deviceID
        self.filename = filename
        self.fileGUID = fileGUID
        self.sHA256Hash = sHA256Hash
        self.fileLocation = fileLocation
        self.fileExpiration = fileExpiration
        self.fileSize = fileSize
        self.fileInS3 = fileInS3
        self.creationDate = creationDate
        self.createdBy = createdBy
        self.lastModifiedDate = lastModifiedDate
        self.lastModifiedBy = lastModifiedBy


class VideoClip:

    def __init__(self, key = 0, fileID = 0, tSFileID = 0, videoClipParameters = '', localFilePath = '', height = 0, width = 0, framesPerSecond: float = 0, bitrate = 0, audioStatus = 0, startTime = 0, startTimeMs = 0, endTime = 0, endTimeMs = 0, clipLengthInSeconds: float = 0):
        self.videoClipID = key
        self.fileID = fileID
        self.tSFileID = tSFileID
        self.videoClipParameters = videoClipParameters
        self.localFilePath = localFilePath
        self.height = height
        self.width = width
        self.framesPerSecond = framesPerSecond
        self.bitrate = bitrate
        self.audioStatus = audioStatus
        self.startTime = startTime
        self.startTimeMs = startTimeMs
        self.endTime = endTime
        self.endTimeMs = endTimeMs
        self.clipLengthInSeconds = clipLengthInSeconds


class TranscodingParameters:

    def __init__(self, fileID: int, source: str, sourceFile: str, targetFile: str, fps: float, codec: str):
        self.fileID = fileID
        self.source = source
        self.sourceFile = sourceFile
        self.targetFile = targetFile
        self.fps = fps
        self.codec = codec


class TransferArgs:

    def __init__(self, fileID: int, videoClipID: int, localFilePath: str, remoteFilename: str, remoteFolderPath: str):
        self.fileID = fileID
        self.videoClipID = videoClipID
        self.localFilePath = localFilePath
        self.remoteFilename = remoteFilename
        self.remoteFolderPath = remoteFolderPath