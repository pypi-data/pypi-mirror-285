if [[ -z ${NO_CLEAN} ]]; then
#  if [[ -z ${SDRTERM_EXEC} ]]; then
#    echo "SDRTERM_EXEC must be specified if a clean install is being used.";
#    exit 1;
#  fi
  deactivate 2>&1 > /dev/null;
  cd /tmp && rm -rf .venv && python -m venv .venv && . .venv/bin/activate && cd ~/sdrterm \
    && PIP_NO_BINARY="" pip install . --upgrade;
fi

if [[ -z ${DSD_CMD} ]]; then
  DSD_CMD="dsd -q -i - -o /dev/null -n";
fi

if [[ -z ${OUT_PATH} ]]; then
  OUT_PATH=/tmp;
fi

if [[ -z ${SDRTERM_EXEC} ]]; then
  SDRTERM_EXEC="python -m sdrterm";
fi

export DSD_CMD="$DSD_CMD";
export OUT_PATH="$OUT_PATH";
export SDRTERM_EXEC="$SDRTERM_EXEC";

echo "$OUT_PATH";
echo "$DSD_CMD";
echo "$SDRTERM_EXEC";

setBlue=$(tput setaf 1);# interestingly, red = R|G|B = 1|0|0.
setNormal=$(tput sgr0);

declare -A sums;

sums["${OUT_PATH}/outB.wav"]="ba12b0bddc0496c7926c21bd89574a0a";
sums["${OUT_PATH}/outd-B.wav"]="15232187d1e2edc76e9a3f6b4cf8288f";
sums["${OUT_PATH}/outd.wav"]="15232187d1e2edc76e9a3f6b4cf8288f";
sums["${OUT_PATH}/outf-B.wav"]="a1a2a4a87cc5c26882527f794b5879a3";
sums["${OUT_PATH}/outf.wav"]="a1a2a4a87cc5c26882527f794b5879a3";
sums["${OUT_PATH}/outh-B.wav"]="9617f6cf9e88cb291cf52416d32e1216";
sums["${OUT_PATH}/outh.wav"]="9617f6cf9e88cb291cf52416d32e1216";
sums["${OUT_PATH}/outi-B.wav"]="a1a2a4a87cc5c26882527f794b5879a3";
sums["${OUT_PATH}/outi.wav"]="a1a2a4a87cc5c26882527f794b5879a3";
sums["${OUT_PATH}/outi16.wav"]="b7b7a07c4d65f1b5c8020730480a6156";
sums["${OUT_PATH}/outu8.wav"]="a4344edc3f13c1036b347c1351923129";
sums["${OUT_PATH}/outi16X.wav"]="b7b7a07c4d65f1b5c8020730480a6156";
#sums["${OUT_PATH}/outB.wav"]="b8058749ff0e25eab70f92dda86c2507";
#sums["${OUT_PATH}/outd.wav"]="d51e36787d2cf8a10be87a1e123bb976";
#sums["${OUT_PATH}/outf.wav"]="07e31be2ff4f16b91adcf540a570c03e";
#sums["${OUT_PATH}/outh.wav"]="576409e4a3cd5e76950aa0134389d75a";
#sums["${OUT_PATH}/outi.wav"]="07e31be2ff4f16b91adcf540a570c03e";

#sums["${OUT_PATH}/outd-B.wav"]="d51e36787d2cf8a10be87a1e123bb976";
#sums["${OUT_PATH}/outf-B.wav"]="07e31be2ff4f16b91adcf540a570c03e";
#sums["${OUT_PATH}/outh-B.wav"]="576409e4a3cd5e76950aa0134389d75a";
#sums["${OUT_PATH}/outi-B.wav"]="07e31be2ff4f16b91adcf540a570c03e";

#sums["${OUT_PATH}/outi16.wav"]="9f21f81dd274b3695adbb0418f787b48";
#sums["${OUT_PATH}/outu8.wav"]="18f1c6cbe373121a3f4c1bfe9f282467";

function cleanup {
  for i in "${!sums[@]}"; do
    if [[ $i == *"tmp"* ]]; then
      rm "$i";
    fi
  done
  deactivate 2>&1 > /dev/null;
}
trap cleanup EXIT;

TEMP=$DSD_CMD
export DSD_CMD="${DSD_CMD} -f1";
coproc SIMO {
  time ./example_simo_file.sh -i /mnt/d/uint8.wav --vfos=15000,-60000 -w5k -c-3.5E+5 -t155.685M -vv -d64 2>&1
}

ts="";
while IFS= ; read -r line; do
  if [[ $line == *"real"* ]] || [[ $line == *"user"* ]] || [[ $line == *"sys"* ]]; then
    echo $line;
  elif [[ $line == *"timestamp"* ]]; then
    ts=$(echo $line | grep "timestamp" - | sed -E "s/^.*: timestamp: ([0-9]+)$/\1/g");
    echo "${OUT_PATH}/out-155625000-${ts}.wav";
    echo "${OUT_PATH}/out-155685000-${ts}.wav";
    echo "${OUT_PATH}/out-155700000-${ts}.wav";
  fi
done <&"${SIMO[0]}"

sums["${OUT_PATH}/out-155625000-${ts}.wav"]="71271e8aae4cff7f00a144acb4a8a8eb";
sums["${OUT_PATH}/out-155685000-${ts}.wav"]="fca67676a496e18a18c4976deb8927b6";
sums["${OUT_PATH}/out-155700000-${ts}.wav"]="c9a2edabd20bf7ad764248c03b6b398d";
#sums["${OUT_PATH}/out-155625000-${ts}.wav"]="38acd5677b3e813eea185523d47b9076";
#sums["${OUT_PATH}/out-155685000-${ts}.wav"]="4cae5a0dfbbe4bd06ea4de41988bd606";
#sums["${OUT_PATH}/out-155700000-${ts}.wav"]="2eaa5e1e736f3b68e67c3b89d1407e1e";

wait $SIMO_PID;
ret=${?};
echo "sdrterm returned: ${ret}";
export DSD_CMD="${TEMP} -fr";

./example.sh /mnt/d/SDRSharp_20160101_231914Z_12kHz_IQ.wav;

declare -A z="( `sed -E "s/^((\d|\w)+)\s*((\d|\w|\/|\-|\.)+)$/[\3]=\1/g" <<< $(md5sum ${OUT_PATH}/*.wav)` )";
for i in "${!sums[@]}"; do
  if [[ "${sums["$i"]}" == "${z["$i"]}" ]]; then
    echo "checksum matched: ${i}"
  else
    printf "${setBlue}FAILED: ${i}\n\tEXPECTED: ${sums["$i"]}\n\tRECEIVED: ${z["$i"]}\n${setNormal}" 1>&2;
  fi
done

exit $ret;
