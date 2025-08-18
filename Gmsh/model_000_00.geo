SetFactory("OpenCASCADE");
Merge "model_000_00.step";

// scale factor（mm → m）
scaleFactor = 1e-3;

allPoints[] = Point "*";
allCurves[] = Curve "*";
allSurfaces[] = Surface "*";
allVolumes[] = Volume "*";

// Scaling
Dilate {{0, 0, 0}, scaleFactor} {
  Point{allPoints[]};
  Curve{allCurves[]};
  Surface{allSurfaces[]};
  Volume{allVolumes[]};
}

// MeshSize
Mesh.CharacteristicLengthMin = 0.01;
Mesh.CharacteristicLengthMax = 0.02;

//+
Physical Surface("IN1", 33) = {5};
//+
Physical Surface("OUT1", 34) = {15};
//+
Physical Surface("WALL", 35) = {1,2,3,4,6,7,8,9,10,11,12,13,14};
