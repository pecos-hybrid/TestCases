# Pointwise V17.1R2 Journal file - Mon Aug 29 13:53:39 2016

package require PWI_Glyph 2.17.1

pw::Application setUndoMaximumLevels 5
pw::Application reset
pw::Application markUndoLevel {Journal Reset}
pw::Application clearModified


### PEARSON FFS w/ NO STEP ###
# 4*pi = 12.566370614359172

# domain points
set pi 3.141592653589793
set delta 1.0
#set Lx [expr 8.0*$pi*$delta]
#set Lz [expr 3.0*$pi*$delta]
set Lx [expr 2.0*$pi*$delta]
set Lz [expr 1.0*$pi*$delta]
set Ly [expr 2.0*$delta]
set p1 "0.0 0.0 0.0" 
set p2 "$Lx 0.0 0.0"
set p3 "$Lx $Ly 0.0"
set p4 "0.0 $Ly 0.0"

# mesh dimensions
#set xnum 300
#set ynum 100
#set znum 100

# small version
set xnum 100 
set ynum 150
set znum 40

# if 2d or 3d
#set xnum 20
#set znum 1

# where to save
set su2File "./channel_mesh.su2"

# mesh sizes
set yini 2.0e-4


### AND BEGIN...

# create domain

set _TMP(mode_10) [pw::Application begin Create]
  set _TMP(PW_24) [pw::SegmentSpline create]
  $_TMP(PW_24) addPoint [subst {$p1}]
  $_TMP(PW_24) addPoint [subst {$p2}]
  set _TMP(con_1) [pw::Connector create]
  $_TMP(con_1) addSegment $_TMP(PW_24)
  unset _TMP(PW_24)
  $_TMP(con_1) calculateDimension
$_TMP(mode_10) end
unset _TMP(mode_10)
pw::Application markUndoLevel {Create 2 Point Connector}

set _TMP(mode_10) [pw::Application begin Create]
  set _CN(1) [pw::GridEntity getByName "con-1"]
  set _TMP(PW_25) [pw::SegmentSpline create]
  $_TMP(PW_25) addPoint [$_CN(1) getPosition -arc 1]
  $_TMP(PW_25) addPoint [subst {$p3}]
  unset _TMP(con_1)
  set _TMP(con_2) [pw::Connector create]
  $_TMP(con_2) addSegment $_TMP(PW_25)
  unset _TMP(PW_25)
  $_TMP(con_2) calculateDimension
$_TMP(mode_10) end
unset _TMP(mode_10)
pw::Application markUndoLevel {Create 2 Point Connector}

set _TMP(mode_10) [pw::Application begin Create]
  set _CN(2) [pw::GridEntity getByName "con-2"]
  set _TMP(PW_26) [pw::SegmentSpline create]
  $_TMP(PW_26) addPoint [$_CN(2) getPosition -arc 1]
  $_TMP(PW_26) addPoint [subst {$p4}]
  unset _TMP(con_2)
  set _TMP(con_3) [pw::Connector create]
  $_TMP(con_3) addSegment $_TMP(PW_26)
  unset _TMP(PW_26)
  $_TMP(con_3) calculateDimension
$_TMP(mode_10) end
unset _TMP(mode_10)
pw::Application markUndoLevel {Create 2 Point Connector}

set _TMP(mode_10) [pw::Application begin Create]
  set _CN(3) [pw::GridEntity getByName "con-3"]
  set _TMP(PW_27) [pw::SegmentSpline create]
  $_TMP(PW_27) addPoint [$_CN(3) getPosition -arc 1]
  $_TMP(PW_27) addPoint [$_CN(1) getPosition -arc 0]
  unset _TMP(con_3)
  set _TMP(con_4) [pw::Connector create]
  $_TMP(con_4) addSegment $_TMP(PW_27)
  unset _TMP(PW_27)
  $_TMP(con_4) calculateDimension
$_TMP(mode_10) end
unset _TMP(mode_10)
pw::Application markUndoLevel {Create 2 Point Connector}



# parition connectors
#  
set _CN(1) [pw::GridEntity getByName "con-1"]
set _TMP(mode_1) [pw::Application begin Dimension]
  set _TMP(PW_1) [pw::Collection create]
  $_TMP(PW_1) set [list $_CN(1)]
  $_TMP(PW_1) do resetGeneralDistributions
  $_TMP(PW_1) do setDimension $xnum
  $_TMP(PW_1) delete
  unset _TMP(PW_1)
  $_TMP(mode_1) balance -resetGeneralDistributions
  set _CN(2) [pw::GridEntity getByName "con-3"]
  set _TMP(PW_2) [pw::Collection create]
  $_TMP(PW_2) set [list $_CN(2)]
  $_TMP(PW_2) do resetGeneralDistributions
  $_TMP(PW_2) do setDimension $xnum
  $_TMP(PW_2) delete
  unset _TMP(PW_2)
  $_TMP(mode_1) balance -resetGeneralDistributions
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Dimension}

set _CN(3) [pw::GridEntity getByName "con-4"]
set _TMP(mode_2) [pw::Application begin Dimension]
  set _TMP(PW_3) [pw::Collection create]
  $_TMP(PW_3) set [list $_CN(3)]
  $_TMP(PW_3) do resetGeneralDistributions
  $_TMP(PW_3) do setDimension $ynum
  $_TMP(PW_3) delete
  unset _TMP(PW_3)
  $_TMP(mode_2) balance -resetGeneralDistributions
  set _CN(4) [pw::GridEntity getByName "con-2"]
  set _TMP(PW_4) [pw::Collection create]
  $_TMP(PW_4) set [list $_CN(4)]
  $_TMP(PW_4) do resetGeneralDistributions
  $_TMP(PW_4) do setDimension $ynum
  $_TMP(PW_4) delete
  unset _TMP(PW_4)
  $_TMP(mode_2) balance -resetGeneralDistributions
$_TMP(mode_2) end
unset _TMP(mode_2)
pw::Application markUndoLevel {Dimension}

set _TMP(mode_3) [pw::Application begin Modify [list $_CN(3)]]
  [[$_CN(3) getDistribution 1] getEndSpacing] setValue $yini
$_TMP(mode_3) end
unset _TMP(mode_3)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_4) [pw::Application begin Modify [list $_CN(3)]]
$_TMP(mode_4) end
unset _TMP(mode_4)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_5) [pw::Application begin Modify [list $_CN(3)]]
$_TMP(mode_5) end
unset _TMP(mode_5)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_6) [pw::Application begin Modify [list $_CN(3)]]
$_TMP(mode_6) abort
unset _TMP(mode_6)

set _CN(1) [pw::GridEntity getByName "con-4"]
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1)]]
  [[$_CN(1) getDistribution 1] getBeginSpacing] setValue $yini
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_2) [pw::Application begin Modify [list $_CN(1)]]
$_TMP(mode_2) end
unset _TMP(mode_2)
pw::Application markUndoLevel {Distribute}

set _CN(2) [pw::GridEntity getByName "con-2"]
set _TMP(mode_3) [pw::Application begin Modify [list $_CN(2)]]
  [[$_CN(2) getDistribution 1] getBeginSpacing] setValue $yini
  [[$_CN(2) getDistribution 1] getEndSpacing] setValue $yini
$_TMP(mode_3) end
unset _TMP(mode_3)
pw::Application markUndoLevel {Distribute}


# mesh area
#  
set _TMP(mode_4) [pw::Application begin Create]
  set _CN(3) [pw::GridEntity getByName "con-1"]
  set _TMP(edge_1) [pw::Edge create]
  $_TMP(edge_1) addConnector $_CN(3)
  set _TMP(edge_2) [pw::Edge create]
  $_TMP(edge_2) addConnector $_CN(2)
  set _CN(4) [pw::GridEntity getByName "con-3"]
  set _TMP(edge_3) [pw::Edge create]
  $_TMP(edge_3) addConnector $_CN(4)
  set _TMP(edge_4) [pw::Edge create]
  $_TMP(edge_4) addConnector $_CN(1)
  set _TMP(dom_1) [pw::DomainStructured create]
  $_TMP(dom_1) addEdge $_TMP(edge_1)
  $_TMP(dom_1) addEdge $_TMP(edge_2)
  $_TMP(dom_1) addEdge $_TMP(edge_3)
  $_TMP(dom_1) addEdge $_TMP(edge_4)
  unset _TMP(edge_4)
  unset _TMP(edge_3)
  unset _TMP(edge_2)
  unset _TMP(edge_1)
$_TMP(mode_4) end
unset _TMP(mode_4)
unset _TMP(dom_1)
pw::Application markUndoLevel {Assemble Domain}

set _TMP(mode_5) [pw::Application begin Create]
$_TMP(mode_5) abort
unset _TMP(mode_5)


# extrude to 3d
#  
set _TMP(mode_6) [pw::Application begin Create]
  set _DM(1) [pw::GridEntity getByName "dom-1"]
  set _TMP(PW_1) [pw::FaceStructured createFromDomains [list $_DM(1)]]
  set _TMP(face_1) [lindex $_TMP(PW_1) 0]
  unset _TMP(PW_1)
  set _TMP(extStrBlock_1) [pw::BlockStructured create]
  $_TMP(extStrBlock_1) addFace $_TMP(face_1)
$_TMP(mode_6) end
unset _TMP(mode_6)
set _TMP(mode_7) [pw::Application begin ExtrusionSolver [list $_TMP(extStrBlock_1)]]
  $_TMP(mode_7) setKeepFailingStep true
  $_TMP(extStrBlock_1) setExtrusionSolverAttribute Mode Translate
  $_TMP(extStrBlock_1) setExtrusionSolverAttribute TranslateDirection {1 0 0}
  set _BL(1) [pw::GridEntity getByName "blk-1"]
  $_TMP(extStrBlock_1) setExtrusionSolverAttribute TranslateDirection {0 0 1}
  $_TMP(extStrBlock_1) setExtrusionSolverAttribute TranslateDistance $Lz
  $_TMP(mode_7) run $znum
$_TMP(mode_7) end
unset _TMP(mode_7)
unset _TMP(extStrBlock_1)
unset _TMP(face_1)
pw::Application markUndoLevel {Extrude, Translate}


# assign bc's
#

# Appended by Pointwise V18.0R2 - Sun Oct  8 20:12:09 2017

pw::Display setShowDomains 0
pw::Display setProjection Perspective
#pw::Application setCAESolver {ANSYS Fluent} 3
pw::Application setCAESolver {Stanford ADL/SU2} 3
pw::Application markUndoLevel {Select Solver}


#set _TMP(mode_9) [pw::Application begin CaeExport [pw::Entity sort [list $_DM(1)]]]
#  $_TMP(mode_9) initialize -strict -type CAE $su2File
#  $_TMP(mode_9) setAttribute FilePrecision Double
#  $_TMP(mode_9) verify
#  $_TMP(mode_9) write
#$_TMP(mode_9) end
#unset _TMP(mode_9)

# Appended by Pointwise V18.0R4 - Fri Feb 23 20:14:05 2018

set _DM(1) [pw::GridEntity getByName "dom-1"]
set _BL(1) [pw::GridEntity getByName "blk-1"]
set _DM(2) [pw::GridEntity getByName "dom-2"]
set _DM(3) [pw::GridEntity getByName "dom-3"]
set _DM(4) [pw::GridEntity getByName "dom-4"]
set _DM(5) [pw::GridEntity getByName "dom-5"]
set _DM(6) [pw::GridEntity getByName "dom-6"]
set _TMP(PW_6) [pw::BoundaryCondition getByName {Unspecified}]
set _TMP(PW_7) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_8) [pw::BoundaryCondition getByName {bc-2}]
unset _TMP(PW_7)
$_TMP(PW_8) apply [list [list $_BL(1) $_DM(5)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_8) setName "left"
pw::Application markUndoLevel {Name BC}

set _TMP(PW_9) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_10) [pw::BoundaryCondition getByName {bc-3}]
unset _TMP(PW_9)
$_TMP(PW_10) apply [list [list $_BL(1) $_DM(3)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_10) setName "right"
pw::Application markUndoLevel {Name BC}

set _TMP(PW_11) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_12) [pw::BoundaryCondition getByName {bc-4}]
unset _TMP(PW_11)
$_TMP(PW_12) setName "bottom"
pw::Application markUndoLevel {Name BC}

$_TMP(PW_12) apply [list [list $_BL(1) $_DM(2)]]
pw::Application markUndoLevel {Set BC}

set _TMP(PW_13) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_14) [pw::BoundaryCondition getByName {bc-5}]
unset _TMP(PW_13)
$_TMP(PW_14) setName "top"
pw::Application markUndoLevel {Name BC}

$_TMP(PW_14) apply [list [list $_BL(1) $_DM(4)]]
pw::Application markUndoLevel {Set BC}

set _TMP(PW_15) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_16) [pw::BoundaryCondition getByName {bc-6}]
unset _TMP(PW_15)
$_TMP(PW_16) setName "front"
pw::Application markUndoLevel {Name BC}

$_TMP(PW_16) apply [list [list $_BL(1) $_DM(6)]]
pw::Application markUndoLevel {Set BC}

set _TMP(PW_17) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_18) [pw::BoundaryCondition getByName {bc-7}]
unset _TMP(PW_17)
$_TMP(PW_18) apply [list [list $_BL(1) $_DM(1)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_18) setName "back"
pw::Application markUndoLevel {Name BC}

unset _TMP(PW_6)
unset _TMP(PW_8)
unset _TMP(PW_10)
unset _TMP(PW_12)
unset _TMP(PW_14)
unset _TMP(PW_16)
unset _TMP(PW_18)
set _TMP(PW_19) [pw::BoundaryCondition getByName {Unspecified}]
set _TMP(PW_20) [pw::BoundaryCondition getByName {left}]
set _TMP(PW_21) [pw::BoundaryCondition getByName {right}]
set _TMP(PW_22) [pw::BoundaryCondition getByName {bottom}]
set _TMP(PW_23) [pw::BoundaryCondition getByName {top}]
set _TMP(PW_24) [pw::BoundaryCondition getByName {front}]
set _TMP(PW_25) [pw::BoundaryCondition getByName {back}]
pw::Display resetView -Z
unset _TMP(PW_19)
unset _TMP(PW_20)
unset _TMP(PW_21)
unset _TMP(PW_22)
unset _TMP(PW_23)
unset _TMP(PW_24)
unset _TMP(PW_25)
set _TMP(PW_26) [pw::BoundaryCondition getByName {Unspecified}]
unset _TMP(PW_26)
set _TMP(PW_27) [pw::BoundaryCondition getByName {left}]
unset _TMP(PW_27)
set _TMP(PW_28) [pw::BoundaryCondition getByName {right}]
unset _TMP(PW_28)
set _TMP(PW_29) [pw::BoundaryCondition getByName {bottom}]
unset _TMP(PW_29)
set _TMP(PW_30) [pw::BoundaryCondition getByName {top}]
unset _TMP(PW_30)
set _TMP(PW_31) [pw::BoundaryCondition getByName {front}]
unset _TMP(PW_31)
set _TMP(PW_32) [pw::BoundaryCondition getByName {back}]
unset _TMP(PW_32)
set _TMP(mode_1) [pw::Application begin CaeExport [pw::Entity sort [list $_BL(1)]]]
  $_TMP(mode_1) initialize -strict -type CAE {/home/oliver/Repos/git/TestCases/hybrid/channel/channel_mesh_100x150x40.su2}
  $_TMP(mode_1) setAttribute FilePrecision Double
  $_TMP(mode_1) verify
  $_TMP(mode_1) write
$_TMP(mode_1) end
unset _TMP(mode_1)
