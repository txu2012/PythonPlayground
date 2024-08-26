:@echo off
:python3 ArduinoControlScript.py %*
:pause

@echo off
SET "comport=\\.\CNCA0"
SET "timebased=N"
SET /A duration = 60 
SET /A loops = 10 
SET /A velocity = 10000
SET /A acceleration = 100000
SET /A axis = 0
python3 ArduinoControlScript.py "%comport%" "%timebased%" %duration% %loops% %velocity% %acceleration% %axis%
pause