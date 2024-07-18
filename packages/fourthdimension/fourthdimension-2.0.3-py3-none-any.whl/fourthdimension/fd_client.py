import jpype
import os
import signal

CHUNK_EMBEDDING = 0x01

SENTENCE_EMBEDDING = 0x02

SUMMARIZING = 0x04

CHUNK_SUMMARIZING = 0x08

SELF_ASKING = 0x10

CHUNK_SELF_ASKING = 0x20

jvmPath = jpype.getDefaultJVMPath()
PATH = "-Djava.class.path=./resources/fourthdimensionclient-2.0.3.jar"
jpype.startJVM(jvmPath, "-ea", PATH)

# # 导入Java类
FourthDimensionClient = jpype.JClass('cn.yantu.fd.FdClient')
fd = FourthDimensionClient()


def getKBInfo(KBName):
    return fd.getKBInfo(KBName)


def createKB(KBName):
    return fd.createKB(KBName)


def deleteKB(KBName):
    return fd.deleteKB(KBName)


def importDocuments(KBName, pathName, rumination):
    return fd.importDocuments(KBName, pathName, rumination)


def addDocument(KBName, sourceFileName, targetFileName, rumination):
    return fd.addDocument(KBName, sourceFileName, targetFileName, rumination)


def deleteDocument(KBName, targetFileName):
    return fd.deleteDocument(KBName, targetFileName)


def updateDocument(kbName, sourceFileName, targetFileName, rumination):
    return fd.updateDocument(kbName, sourceFileName, targetFileName, rumination)


def query(KBName, question):
    return fd.query(KBName, question)


def ruminate(KBName, rumination):
    return fd.ruminate(KBName, rumination)


def queryByText(KBName, question):
    return fd.queryByText(KBName, question)


def queryByTextBleu(KBName, question):
    return fd.queryByTextBleu(KBName, question)


def queryByTextSentenceBleu(KBName, question):
    return fd.queryByTextSentenceBleu(KBName, question)


def queryByTextVectorBleu(KBName, question):
    return fd.queryByTextVectorBleu(KBName, question)


def exitFD():
    os.kill(os.getpid(), signal.SIGINT)


# # 完成后关闭JVM
if __name__ == '__main__':
    jvmPath = jpype.getDefaultJVMPath()
    print(jvmPath)
    jpype.java.lang.System.out.println("hello world!")
    getKBInfo("test")
    exitFD()
    # jpype.ShutdownJVM()
