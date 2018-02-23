# Create mesh of 2d channel
package require PWI_Glyph 2.18.0

# Number of points in x and y
set Nx 33
set Ny 129

# Output file name
set su2File "./channel_mesh.su2"

# Convenience
set pi [expr {acos(-1.0)}]

set Lx [expr {2.0*$pi}]

# Corners of domain
set p0 "0 0 0"
set p1 "$Lx 0 0"
set p2 "$Lx 2 0"
set p3 "0 2 0"

# Desired spacing at first mesh point off the wall
set yp0 "0.0004"

# Pointwise foo
pw::Application setUndoMaximumLevels 5
pw::Application reset
pw::Application clearModified


# Create the connectors that define the geometry
set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(PW_1) [pw::SegmentSpline create]
  $_TMP(PW_1) addPoint $p0
  $_TMP(PW_1) addPoint $p1
  set _TMP(con_1) [pw::Connector create]
  $_TMP(con_1) addSegment $_TMP(PW_1)
  unset _TMP(PW_1)
  $_TMP(con_1) calculateDimension
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Create 2 Point Connector}

set _TMP(mode_2) [pw::Application begin Create]
  set _TMP(PW_2) [pw::SegmentSpline create]
  $_TMP(PW_2) addPoint $p1
  $_TMP(PW_2) addPoint $p2
  unset _TMP(con_1)
  set _TMP(con_2) [pw::Connector create]
  $_TMP(con_2) addSegment $_TMP(PW_2)
  unset _TMP(PW_2)
  $_TMP(con_2) calculateDimension
$_TMP(mode_2) end
unset _TMP(mode_2)
pw::Application markUndoLevel {Create 2 Point Connector}

set _TMP(mode_3) [pw::Application begin Create]
  set _TMP(PW_3) [pw::SegmentSpline create]
  $_TMP(PW_3) addPoint $p2
  $_TMP(PW_3) addPoint $p3
  unset _TMP(con_2)
  set _TMP(con_3) [pw::Connector create]
  $_TMP(con_3) addSegment $_TMP(PW_3)
  unset _TMP(PW_3)
  $_TMP(con_3) calculateDimension
$_TMP(mode_3) end
unset _TMP(mode_3)
pw::Application markUndoLevel {Create 2 Point Connector}

set _TMP(mode_4) [pw::Application begin Create]
  set _TMP(PW_4) [pw::SegmentSpline create]
  $_TMP(PW_4) addPoint $p3
  $_TMP(PW_4) addPoint $p0
  unset _TMP(con_3)
  set _TMP(con_4) [pw::Connector create]
  $_TMP(con_4) addSegment $_TMP(PW_4)
  unset _TMP(PW_4)
  $_TMP(con_4) calculateDimension
$_TMP(mode_4) end
unset _TMP(mode_4)
pw::Application markUndoLevel {Create 2 Point Connector}


# Dimension the connectors
set _CN(1) [pw::GridEntity getByName "con-3"]
set _CN(2) [pw::GridEntity getByName "con-1"]
set _TMP(PW_6) [pw::Collection create]
$_TMP(PW_6) set [list $_CN(1) $_CN(2)]
$_TMP(PW_6) do setDimension $Nx
$_TMP(PW_6) delete
unset _TMP(PW_6)
pw::Application markUndoLevel {Dimension}

set _CN(3) [pw::GridEntity getByName "con-4"]
set _CN(4) [pw::GridEntity getByName "con-2"]
set _TMP(PW_7) [pw::Collection create]
$_TMP(PW_7) set [list $_CN(3) $_CN(4)]
$_TMP(PW_7) do setDimension $Ny
$_TMP(PW_7) delete
unset _TMP(PW_7)
pw::Application markUndoLevel {Dimension}

# Create a domain
set _TMP(PW_8) [pw::DomainStructured createFromConnectors -reject _TMP(unusedCons) -solid [list $_CN(1) $_CN(3) $_CN(2) $_CN(4)]]
unset _TMP(unusedCons)
unset _TMP(PW_8)
pw::Application markUndoLevel {Assemble Domains}

# Set spacing constraints
set _TMP(mode_6) [pw::Application begin Modify [list $_CN(3) $_CN(4)]]
  $_CN(3) setDistribution 1 [pw::DistributionTanh create]
  $_CN(4) setDistribution 1 [pw::DistributionTanh create]
  [[$_CN(3) getDistribution 1] getEndSpacing] setValue $yp0
  [[$_CN(3) getDistribution 1] getBeginSpacing] setValue $yp0
  [[$_CN(4) getDistribution 1] getBeginSpacing] setValue $yp0
  [[$_CN(4) getDistribution 1] getEndSpacing] setValue $yp0
$_TMP(mode_6) end
unset _TMP(mode_6)
pw::Application markUndoLevel {Distribute}

# Select SU2, 2D
pw::Application setCAESolver {Stanford ADL/SU2} 2
pw::Application markUndoLevel {Set Dimension 2D}

# Specify boundary names
set _DM(1) [pw::GridEntity getByName "dom-1"]
set _TMP(PW_9) [pw::BoundaryCondition getByName {Unspecified}]
set _TMP(PW_10) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_11) [pw::BoundaryCondition getByName {bc-2}]
unset _TMP(PW_10)
$_TMP(PW_11) apply [list [list $_DM(1) $_CN(1)] [list $_DM(1) $_CN(2)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_11) setName "Wall"
pw::Application markUndoLevel {Name BC}

set _TMP(PW_12) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_13) [pw::BoundaryCondition getByName {bc-3}]
unset _TMP(PW_12)
$_TMP(PW_13) apply [list [list $_DM(1) $_CN(3)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_13) setName "Inlet"
pw::Application markUndoLevel {Name BC}

set _TMP(PW_14) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_15) [pw::BoundaryCondition getByName {bc-4}]
unset _TMP(PW_14)
$_TMP(PW_15) apply [list [list $_DM(1) $_CN(4)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_15) setName "Outlet"
pw::Application markUndoLevel {Name BC}

unset _TMP(PW_9)
unset _TMP(PW_11)
unset _TMP(PW_13)
unset _TMP(PW_15)
set _TMP(PW_16) [pw::BoundaryCondition getByName {Unspecified}]
unset _TMP(PW_16)
set _TMP(PW_17) [pw::BoundaryCondition getByName {Wall}]
unset _TMP(PW_17)
set _TMP(PW_18) [pw::BoundaryCondition getByName {Inlet}]
unset _TMP(PW_18)
set _TMP(PW_19) [pw::BoundaryCondition getByName {Outlet}]
unset _TMP(PW_19)
set _TMP(mode_9) [pw::Application begin CaeExport [pw::Entity sort [list $_DM(1)]]]
  $_TMP(mode_9) initialize -strict -type CAE $su2File
  $_TMP(mode_9) setAttribute FilePrecision Double
  $_TMP(mode_9) verify
  $_TMP(mode_9) write
$_TMP(mode_9) end
unset _TMP(mode_9)
