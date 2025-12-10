"""
    Build script for test.py
    test-builder.py
"""

import sys
from os.path import join, getsize
from platform import system

from SCons.Script import Default, DefaultEnvironment

env = DefaultEnvironment()
board_config = env.BoardConfig()

# print the size of the binary programming file
def sizePrintCMD(target, source, env):
  print("\nSize of %s:\n\t-- %s bytes (%s words) --\n" % (source[0], source[0].get_size(), int(source[0].get_size()/2)))

# A full list with the available variables
# http://www.scons.org/doc/production/HTML/scons-user.html#app-variables
env.Replace(
 #   AR="sdar",
    CC="sdcc",
    OBJCOPY="makebin",
    RANLIB="sdranlib",
    OBJSUFFIX=".rel",
    SIZETOOL="cat",     # use cat to get content from map file for size calculations
    TARGET_VDD_MV=round(1000*float(board_config.get("build.calibration_voltage"))), #get calibration voltage in mV

    # CFLAGS=[
    #     "-m%s" % board_config.get("build.cpu"),
    #     "--std-sdcc11",
    #     "--opt-code-size"
    # ],

    # CPPDEFINES=[
    #     "F_CPU=$BOARD_F_CPU",
    #     "TARGET_VDD_MV=$TARGET_VDD_MV",
    #     "$BOARD_MCU"
    # ],

    # LINKFLAGS=[
    #     "-m%s" % board_config.get("build.cpu"),
    #     "--out-fmt-ihx"
    # ],

    BINFILE = join("$BUILD_DIR", "${PROGNAME}.bin"),
    MAPFILE = join("$BUILD_DIR", "${PROGNAME}.map"),
    SIZECHECKCMD=['python', '-c', 'from os.path import getsize; print("CODE = %s" % getsize("${BINFILE}"))'],  # get flash size from bin file
    #SIZECHECKCMD=['${SIZETOOL}', '${MAPFILE}'],
    SIZEPROGREGEXP=r"^(?:CODE|GSINIT|GSFINAL|CONST|HOME|RSEG0|SSEG|HEADER1|HEADER3|PREG2)[^=]*\D+(\d+).*",
    SIZEDATAREGEXP=r"^(?:DATA)[^=]*\D+(\d+).*",

    PROGNAME="firmware",
    PROGSUFFIX=".ihx"
)


#
# Target: Build executable and linkable firmware
#

#target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_ihx = join("$BUILD_DIR", "${PROGNAME}.elf")
    target_bin = join("$BUILD_DIR", "${PROGNAME}.bin")
else:
    target_ihx = env.BuildProgram()
    target_bin = env.Command(
        join("$BUILD_DIR", "${PROGNAME}.bin"),
        target_ihx,
        "$OBJCOPY -p $SOURCES $TARGET"
    )

#
# Target: Print binary size
#

env.AddPlatformTarget(
    name="file_size",
    dependencies=target_bin,
    actions=sizePrintCMD,
    title="Program Size",
    description="Calculate program size"
)

#
# Target: Upload firmware
#

upload_protocol = env.subst("$UPLOAD_PROTOCOL")
upload_port = env.subst("$UPLOAD_PORT")
upload_actions = []


if upload_protocol == "easy-pdk-programmer":
    env.Replace(
        UPLOADER="easypdkprog",
        UPLOADERFLAGS=[
            '-n',
            board_config.get("build.mcu")
        ],
        UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS write $SOURCE'
    )
    if upload_port:
        env.Append(UPLOADERFLAGS=["--port", upload_port])
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]
else:
    sys.stderr.write("Warning! Unknown upload protocol %s\n" % upload_protocol)

AlwaysBuild(env.Alias("upload", target_ihx, upload_actions))


#
# Target: Define targets
#
Default("file_size")