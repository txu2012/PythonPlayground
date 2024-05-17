:@echo off
:python3 ArduinoControlScript.py %*
:pause

@echo off
SET "comport=\\.\CNCA0"
SET "timebased=Y"
SET /A duration = 60 
SET /A loops = 10 
SET /A velocity = 5000
SET /A acceleration = 100000
SET /A axis = 0
python3 ArduinoControlScript.py "%comport%" "%timebased%" %duration% %loops% %velocity% %acceleration% %axis%
pause