import struct
import math
import re

def fsstat_iso9660(f):
	output = []

	# read past System Area
	f.read(32 * 1024)

	FileExtents = []
	DirExtents = []
	volumeDescriptor = f.read(2048)
	while volumeDescriptor[0] != 255:
		if volumeDescriptor[0] == 1:
			fpos = f.tell()
			systemType = volumeDescriptor[8:40].decode().strip()
			volumeName = stripNullBytes(volumeDescriptor[40:72].decode().strip())
			volumeSetSize = struct.unpack("<H", volumeDescriptor[120:122])[0]
			volumeSetSeq = struct.unpack("<H", volumeDescriptor[124:126])[0]
			volumeSpaceSize = struct.unpack("<I", volumeDescriptor[80:84])[0]
			publisher = volumeDescriptor[318:446].decode().strip()
			dataPreparer = volumeDescriptor[446:574].decode().strip()
			recordingApp = volumeDescriptor[574:702].decode().strip()
			copyright = volumeDescriptor[702:740].decode().strip()
			pathTableSize = struct.unpack("<I", volumeDescriptor[132:136])[0]
			pathTableLocation = struct.unpack(">I", volumeDescriptor[148:152])[0]
			blockSize = struct.unpack("<H", volumeDescriptor[128:130])[0]
			rootDirectoryEntry = volumeDescriptor[156:190]
			rootDirectoryLoc = struct.unpack("<I", rootDirectoryEntry[2:6])[0]
			f.seek(pathTableLocation * blockSize)
			numInodes = calcNumInodes(f, rootDirectoryLoc, blockSize)
			numSectors = math.ceil((blockSize * volumeSpaceSize) / 2048)
			output.append("=== PRIMARY VOLUME DESCRIPTOR 1 ===")
			output.append("FILE SYSTEM INFORMATION")
			output.append("--------------------------------------------")
			output.append("File System Type: ISO9660")
			output.append("Volume Name: " + volumeName)
			output.append("Volume Set Size: " + str(volumeSetSize))
			output.append("Volume Set Sequence: " + str(volumeSetSeq))
			output.append("Publisher: " + publisher)
			output.append("Data Preparer: " + dataPreparer)
			output.append("Recording Application: " + recordingApp)
			output.append("Copyright: " + copyright)
			output.append("")
			output.append("METADATA INFORMATION")
			output.append("--------------------------------------------")
			output.append("Path Table Location: " + str(pathTableLocation) + "-" + str(pathTableLocation + math.ceil(pathTableSize / blockSize) - 1))
			output.append("Inode Range: 0 - " + str(1 + numInodes))
			output.append("Root Directory Block: " + str(rootDirectoryLoc))
			output.append("")
			output.append("CONTENT INFORMATION")
			output.append("--------------------------------------------")
			output.append("Sector Size: 2048")
			output.append("Block Size: " + str(blockSize))
			output.append("Total Sector Range: 0 - " + str(numSectors - 1))
			output.append("Total Block Range: 0 - " + str(volumeSpaceSize - 1))
			f.seek(fpos)
		elif volumeDescriptor[0] == 2:
			fpos = f.tell()
			systemType = volumeDescriptor[8:40].decode("utf-16be").strip()
			volumeName = stripNullBytes(volumeDescriptor[40:72].decode("utf-16be").strip())
			volumeSetSize = struct.unpack("<H", volumeDescriptor[120:122])[0]
			volumeSetSeq = struct.unpack("<H", volumeDescriptor[124:126])[0]
			volumeSpaceSize = struct.unpack("<I", volumeDescriptor[80:84])[0]
			publisher = stripNullBytes(volumeDescriptor[318:446].decode("utf-16be").strip())
			dataPreparer = stripNullBytes(volumeDescriptor[446:574].decode("utf-16be").strip())
			recordingApp = stripNullBytes(volumeDescriptor[574:702].decode("utf-16be").strip())
			copyright = stripNullBytes(volumeDescriptor[702:740].decode())
			pathTableSize = struct.unpack("<I", volumeDescriptor[132:136])[0]
			pathTableLocation = struct.unpack(">I", volumeDescriptor[148:152])[0]
			blockSize = struct.unpack("<H", volumeDescriptor[128:130])[0]
			rootDirectoryEntry = volumeDescriptor[156:190]
			rootDirectoryLoc = struct.unpack("<I", rootDirectoryEntry[2:6])[0]
			jolietEncodingBytes = volumeDescriptor[88:91].decode()
			if jolietEncodingBytes == "%/@":
				jolietEncoding = "Level 1"
			elif jolietEncodingBytes == "%/C":
				jolietEncoding = "Level 2"
			else:
				jolietEncoding = "Level 3"
			numSectors = math.ceil((blockSize * volumeSpaceSize) / 2048)
			output.append("")
			output.append("=== SUPPLEMENTARY VOLUME DESCRIPTOR 1 ===")
			output.append("FILE SYSTEM INFORMATION")
			output.append("--------------------------------------------")
			output.append("File System Type: ISO9660")
			output.append("Volume Name: ")
			output.append("Volume Set Size: " + str(volumeSetSize))
			output.append("Volume Set Sequence: " + str(volumeSetSeq))
			output.append("Publisher: " + publisher)
			output.append("Data Preparer: " + dataPreparer)
			output.append("Recording Application: " + recordingApp)
			output.append("Copyright: " + copyright)
			output.append("")
			output.append("METADATA INFORMATION")
			output.append("--------------------------------------------")
			output.append("Path Table Location: " + str(pathTableLocation) + "-" + str(pathTableLocation + math.ceil(pathTableSize / blockSize) - 1))
			output.append("Root Directory Block: " + str(rootDirectoryLoc))
			output.append("Joliet Name Encoding: UCS-2 " + jolietEncoding)
			output.append("")
			output.append("CONTENT INFORMATION")
			output.append("--------------------------------------------")
			output.append("Sector Size: 2048")
			output.append("Block Size: " + str(blockSize))
			output.append("Total Sector Range: 0 - " + str(numSectors - 1))
			output.append("Total Block Range: 0 - " + str(volumeSpaceSize - 1))
			f.seek(fpos)
		volumeDescriptor = f.read(2048)

	return output		

def calcNumInodes(f, rootDirLoc, blockSize):
	f.seek(rootDirLoc * blockSize)
	lenDirRecord = struct.unpack("<B", f.read(1))[0]
	f.read(lenDirRecord - 1)
	lenDirRecord = struct.unpack("<B", f.read(1))[0]
	f.read(lenDirRecord - 1)
	
	lenDirRecord = struct.unpack("<B", f.read(1))[0]
	f.seek(-1, 1)
	numInodes = 0
	while lenDirRecord != 0:
		numInodes = numInodes + 1
		dirRecord = f.read(lenDirRecord)
		if (dirRecord[25:26] != b'\x02'):
			lenDirRecord = struct.unpack("<B", f.read(1))[0]
			f.seek(-1, 1)
			continue
		extentLocation = struct.unpack("<I", dirRecord[2:6])[0]
		fpos = f.tell()
		numInodes = numInodes + calcNumInodes(f, extentLocation, blockSize)
		f.seek(fpos)
		lenDirRecord = struct.unpack("<B", f.read(1))[0]
		f.seek(-1, 1)
	return numInodes

def stripNullBytes(string):
	for i in range(len(string)):
		if string[i] == '\x00':
			string = string[:i]
			break
	return string

