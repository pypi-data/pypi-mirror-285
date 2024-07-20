# -*- coding: utf-8 -*-
#
# Copyright (c) 1996-2023, SR Research Ltd., All Rights Reserved
#
# For use by SR Research licencees only. Redistribution and use in source
# and binary forms, with or without modification, are NOT permitted.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the distribution.
#
# Neither name of SR Research Ltd nor the name of contributors may be used
# to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS
# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# $Date: 2009/11/02 16:14:37 $
#

"""Performing research with eye-tracking equipment typically requires a long-term investment in software
tools to collect, process, and analyze data. Much of this involves real-time data collection, saccadic
analysis, calibration routines, and so on.
The EyeLink® eye-tracking system is designed to implement most of the required software base for data
collection and conversion. It is most powerful when used with the Ethernet link interface, which allows
remote control of data collection and real-time data transfer. The PyLink toolkit includes Pylink module,
which implements all core EyeLink functions and classes for EyeLink connection and the eyelink graphics,
such as the display of camera image, calibration, validation, and drift correct. The EyeLink graphics is
currently implemented using Simple Direct Media Layer (SDL: www.libsdl.org).


The Pylink library contains a set of classes and functions, which are used to program experiments on many
different platforms, such as MS-DOS, Windows, Linux, and the Macintosh. Some programming standards,
such as placement of messages in the EDF file by your experiment, and the use of special data types, have
been implemented to allow portability of the development kit across platforms. The standard messages
allow general analysis tools such as EDF2ASC converter or EyeLink Data Viewer to process your EDF files.


"""

from constants import *

from pylink_c import inRealTimeMode
from pylink_c import flushGetkeyQueue
from pylink_c import beginRealTimeMode
from pylink_c import currentTime
from pylink_c import currentUsec
#from pylink_c import currentDoubleUsec
from pylink_c import endRealTimeMode
from pylink_c import pumpDelay
from pylink_c import msecDelay
from pylink_c import alert
from pylink_c import enableExtendedRealtime
from pylink_c import getLastError
from pylink_c import enablePCRSample



try:
	from pylink_c import enableUTF8EyeLinkMessages
except:
	#means no win32 defined
	pass
from pylink_c import openCustomGraphicsInternal
from pylink_c import bitmapSave
from pylink_c import sendMessageToFile
from pylink_c import openMessageFile
from pylink_c import closeMessageFile

from tracker import EndBlinkEvent
from tracker import StartBlinkEvent
from tracker import StartNonBlinkEvent
from tracker import FixUpdateEvent
from tracker import StartFixationEvent
from tracker import EndFixationEvent
from tracker import StartSaccadeEvent
from tracker import EndSaccadeEvent
from tracker import EyeLinkAddress
from tracker import EyelinkMessage
from tracker import EyeLinkCustomDisplay
from tracker import KeyInput
from tracker import ILinkData
from tracker import IOEvent
from tracker import ButtonEvent
from tracker import MessageEvent
from tracker import Sample
from tracker import rawSample



from eyelink import EyeLinkListener
from eyelink import EyeLink
from eyelink import getEYELINK
from eyelink import openGraphicsEx




from eyelink import setCalibrationColors
from eyelink import setTargetSize
from eyelink import setCalibrationSounds
from eyelink import setDriftCorrectSounds
from eyelink import setCameraPosition
from eyelink import getDisplayInformation
from eyelink import openGraphics
from eyelink import closeGraphics
from eyelink import resetBackground

from eyelink import setCalibrationAnimationTarget
from eyelink import enableExternalCalibrationDevice



from __version__ import *

