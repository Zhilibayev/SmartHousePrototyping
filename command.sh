#raspivid -o - -t 99999 -w 640 -h 360 -fps 25|cvlc stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}':demux=h264
#raspivid -n -ih -t 0 -w 640 -h 360 -b 1000000 -fps 20 -o - | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:1234/}':demux=h264
#raspivid -n -t 0 -w 640 -h 360 -fps 20 -o - | cvlc -I dummy stream:///dev/stdin --sout '#rtp{rtsp://:8080/}':demux=h264
#raspivid -n -t 0 -fps 30 -w 800 -h 600 -o - | nc 192.168.0.100 2222
raspivid -n -t 0 -w 640 -h 360 -hf -ih -fps 5 -o - | nc -k -l 2222
#raspivid --timeout 99999999 --nopreview --intra 2 --width 1000 --height 500 --framerate 20 --output - -b 1200000 | nc 192.168.0.100 5555
#raspivid -t 999999 --hflip -o - -w 512 -h 512 -fps 15 | nc 192.168.0.100 5555
