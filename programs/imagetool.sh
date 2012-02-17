#!/bin/bash
############################################################################
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
############################################################################

EXIT=0

while [ $EXIT = 0 ]; do
	echo "# Imagetool"
	echo
	echo "# Commands"
	echo "#   create = create an image"
	echo "#   part   = part an image"
	echo "#   format = format a partition"
	echo "#   mount  = mount a partition"
	echo "#   exit   = quit the program"
	echo
	printf "# Command: "
	read COMMAND
	case $COMMAND in
		"create")
			printf "#   Filename: "
			read FILENAME
			printf "#   Size (B, K, M, G): "
			read SIZE
			echo $SIZE | grep "B" >/dev/null
			if [ $? = 0 ]; then
				bs=$(echo $SIZE | sed 's/B//!g')
				count=1
				size=$(echo $SIZE | sed 's/B//!g')
			fi
			echo $SIZE | grep "K" >/dev/null
			if [ $? = 0 ]; then
				bs="1024"
				count=$(echo $SIZE | sed 's/K//g')
				size=$SIZE
			fi
			echo $SIZE | grep "M" >/dev/null
			if [ $? = 0 ]; then
				bs="1048576"
				count=$(echo $SIZE | sed 's/M//g')
				size=$SIZE
			fi
			echo $SIZE | grep "G" >/dev/null
			if [ $? = 0 ]; then
				bs="1073741824"
				count=$(echo $SIZE | sed 's/G//g')
				size=$SIZE
			fi
			dd if=/dev/zero bs=${bs} count=${count} 2>/dev/null | pv -s ${size}  >${FILENAME}
			;;
		"part")
			printf "#   Filename: "
			read FILENAME
			cfdisk ${FILENAME}
			if [ $? != 0 ]; then
				echo "# Error: Wait 5 seconds"
				sleep 5
			fi
			;;
		"format")
			printf "#   Filename: "
			read FILENAME
			if [ ! -f $FILENAME ]; then
				echo "# Error: File doesn't exist"
				echo "# Error: Wait 5 seconds"
				sleep 5
			else
				echo "# Please choose one:"
				fdisk -l ${FILENAME} | sed "s/*//g" | grep "${FILENAME}[0-9]" | while read name start end blocks id system; do
					echo "#   Name: ${name} / System: ${system}"  
				done
				printf "# Name: "
				read NAME
				fdisk -l ${FILENAME} | sed "s/*//g" | grep "${NAME}" >/dev/null
				if [ $? != 0 ]; then
					echo "# Error: ${NAME} doesn't exist"
					echo "# Error: Wait 5 seconds"
					sleep 5
				else
					INFO=($(fdisk -l ${FILENAME} | sed "s/*//g" | grep "${NAME}"))
					FREE=$(losetup --find)
					let offset=${INFO[1]}*512
					losetup -o${offset} ${FREE} ${FILENAME}
					printf "# Type (ext2, ext3, dos): "
					read TYPE
					case $TYPE in
						"ext2")
							mkfs.ext2 -b1024 ${FREE} $(echo ${INFO[3]} | sed "s/+//g")
							;;
						"ext3")
							mkfs.ext3 -b1024 ${FREE} $(echo ${INFO[3]} | sed "s/+//g")
							;;
						"dos")
							mkdosfs -F32 ${FREE} $(echo ${INFO[3]} | sed "s/+//g")
							;;
					esac
					sleep 1
					losetup -d ${FREE}			
				fi
			fi
			;;
		"mount")
			printf "#   Filename: "
			read FILENAME
			if [ ! -f $FILENAME ]; then
				echo "# Error: File doesn't exist"
				echo "# Error: Wait 5 seconds"
				sleep 5
			else
				echo "# Please choose one:"
				fdisk -l ${FILENAME} | sed "s/*//g" | grep "${FILENAME}[0-9]" | while read name start end blocks id system; do
					echo "#   Name: ${name} / System: ${system}"  
				done
				printf "# Name: "
				read NAME
				fdisk -l ${FILENAME} | sed "s/*//g" | grep "${NAME}" >/dev/null
				if [ $? != 0 ]; then
					echo "# Error: ${NAME} doesn't exist"
					echo "# Error: Wait 5 seconds"
					sleep 5
				else
					INFO=($(fdisk -l ${FILENAME} | sed "s/*//g" | grep "${NAME}"))
					let offset=${INFO[1]}*512
					printf "# Target: "
					read TARGET
					if [ ! -d ${TARGET} ]; then
						echo "# Error: ${TARGET} doesn't exist or isn't a directory"
						echo "# Error: Wait 5 seconds"
						sleep 5
					else
						sudo mount -oloop,offset=${offset} ${FILENAME} ${TARGET}
						if [ $? != 0 ]; then
							echo "# Error: Wait 5 seconds"
							sleep 5
						fi
					fi
				fi
			fi
			;;
		"exit")
			EXIT=1
			;;
	esac
done	
