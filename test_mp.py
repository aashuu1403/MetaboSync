import mediapipe as mp
print("Attributes in mp:", dir(mp))
if hasattr(mp, 'solutions'):
    print("SUCCESS: solutions module found!")
else:
    print("FAILED: solutions module missing.")
