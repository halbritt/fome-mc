# AGENTEE-485 J2d post-emission verification recipes (verification only; not pipeline source).
j2d-native:
	timeout 450 python3 -B build/ee485-J2d-native.py
include telemetry-pod/expansion/production-capture/diagnostics/ee485-J2d/validation/ee485-J2d.mk
