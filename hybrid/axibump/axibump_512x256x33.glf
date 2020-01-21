# Pointwise V18.2R2 Journal file - Fri May  3 15:57:28 2019

package require PWI_Glyph 2.18.2

pw::Application setUndoMaximumLevels 5
pw::Application reset
pw::Application markUndoLevel {Journal Reset}

pw::Application clearModified

set _TMP(mode_1) [pw::Application begin GridImport]
  $_TMP(mode_1) initialize -strict -type {PLOT3D} {/home/oliver/Repos/git/TestCases/hybrid/axibump/bump_newaxi_721.p2dfmt}
  $_TMP(mode_1) read
  $_TMP(mode_1) convert
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Import Grid}

set _CN(1) [pw::GridEntity getByName con-1]
set _CN(2) [pw::GridEntity getByName con-3]
set _TMP(PW_1) [pw::Collection create]
$_TMP(PW_1) set [list $_CN(1) $_CN(2)]
$_TMP(PW_1) do setDimension 512
$_TMP(PW_1) delete
unset _TMP(PW_1)
pw::CutPlane refresh
pw::Application markUndoLevel {Dimension}

set _CN(3) [pw::GridEntity getByName con-2]
set _CN(4) [pw::GridEntity getByName con-4]
set _TMP(PW_1) [pw::Collection create]
$_TMP(PW_1) set [list $_CN(3) $_CN(4)]
$_TMP(PW_1) do setDimension 256
$_TMP(PW_1) delete
unset _TMP(PW_1)
pw::CutPlane refresh
pw::Application markUndoLevel {Dimension}

set _DM(1) [pw::GridEntity getByName dom-1]
set _TMP(exam_1) [pw::Examine create "DomainLengthI"]
$_TMP(exam_1) addEntity [list $_DM(1)]
$_TMP(exam_1) examine
pw::CutPlane applyMetric {}
$_TMP(exam_1) delete
unset _TMP(exam_1)
set _TMP(exam_1) [pw::Examine create "DomainLengthJ"]
$_TMP(exam_1) addEntity [list $_DM(1)]
$_TMP(exam_1) examine
pw::CutPlane applyMetric {}
set _TMP(PW_1) [pw::ExamineFilter create]
$_TMP(PW_1) setDecisionLine 1 All
$_TMP(PW_1) removeAllLines
$_TMP(PW_1) setDecisionLine 1 All
$_TMP(PW_1) setEnabled 1 1
$_TMP(PW_1) insertConditionLine 2 {} Equal {}
$_TMP(PW_1) setEnabled 2 1
$_TMP(PW_1) removeAllLines
$_TMP(PW_1) setDecisionLine 1 All
$_TMP(PW_1) setEnabled 1 1
$_TMP(PW_1) insertConditionLine 2 {Length, J} LessThan {1e-5}
$_TMP(PW_1) setEnabled 2 1
$_TMP(exam_1) delete
unset _TMP(exam_1)
unset _TMP(PW_1)
pw::CutPlane applyMetric ""
pw::Application markUndoLevel {Update Examine Filters}

set _TMP(mode_1) [pw::Application begin Dimension]
$_TMP(mode_1) abort
unset _TMP(mode_1)
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1) $_CN(2)]]
  $_CN(1) addBreakPoint -arc 0.484506213477
  $_CN(1) addBreakPoint -control 304
  $_CN(1) addBreakPoint -control 459
  [[$_CN(1) getDistribution 1] getEndSpacing] setValue 0.004
  [[$_CN(1) getDistribution 2] getBeginSpacing] setValue 0.004
  [[$_CN(1) getDistribution 2] getEndSpacing] setValue 0.002
  [[$_CN(1) getDistribution 3] getBeginSpacing] setValue 0.002
  [[$_CN(1) getDistribution 3] getEndSpacing] setValue 0.004
  [[$_CN(1) getDistribution 4] getBeginSpacing] setValue 0.004
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Dimension]
$_TMP(mode_1) abort
unset _TMP(mode_1)
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1)]]
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1)]]
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1)]]
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1)]]
  $_CN(1) setSubConnectorDimension [list 100 64 96 255]
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1)]]
  $_CN(1) setDimensionFromDistribution
  $_CN(1) setDimensionFromDistribution
$_TMP(mode_1) abort
unset _TMP(mode_1)
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1) $_CN(2)]]
  [[$_CN(2) getDistribution 1] getEndSpacing] setValue 0.16
  [[$_CN(2) getDistribution 1] getBeginSpacing] setValue 0.04
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1) $_CN(2)]]
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1) $_CN(2)]]
  [[$_CN(2) getDistribution 1] getEndSpacing] setValue 0.16
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1) $_CN(2)]]
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Modify [list $_CN(3) $_CN(4)]]
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin Modify [list $_CN(3) $_CN(4)]]
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _TMP(mode_1) [pw::Application begin EllipticSolver [list $_DM(1)]]
  set _TMP(exam_1) [pw::Examine create "DomainLengthRatioJ"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  set _TMP(exam_2) [pw::Examine create "DomainLengthJ"]
  $_TMP(exam_2) addEntity [list $_DM(1)]
  $_TMP(exam_2) examine
  $_TMP(exam_2) delete
  unset _TMP(exam_2)
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  set _TMP(exam_1) [pw::Examine create "DomainLengthRatioI"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  set _TMP(exam_2) [pw::Examine create "DomainLengthJ"]
  $_TMP(exam_2) addEntity [list $_DM(1)]
  $_TMP(exam_2) examine
  $_TMP(exam_2) delete
  unset _TMP(exam_2)
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  set _TMP(exam_1) [pw::Examine create "DomainSkewEquiangle"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  set _TMP(exam_2) [pw::Examine create "DomainLengthJ"]
  $_TMP(exam_2) addEntity [list $_DM(1)]
  $_TMP(exam_2) examine
  $_TMP(exam_2) delete
  unset _TMP(exam_2)
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  set _TMP(exam_1) [pw::Examine create "DomainMinimumAngle"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  set _TMP(exam_2) [pw::Examine create "DomainLengthJ"]
  $_TMP(exam_2) addEntity [list $_DM(1)]
  $_TMP(exam_2) examine
  $_TMP(exam_2) delete
  unset _TMP(exam_2)
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  pw::CutPlane applyMetric ""
  $_TMP(mode_1) setActiveSubGrids $_DM(1) [list]
  $_TMP(mode_1) run 10
  $_TMP(mode_1) setActiveSubGrids $_DM(1) [list]
  $_TMP(mode_1) run 10
  $_TMP(mode_1) setActiveSubGrids $_DM(1) [list]
  $_TMP(mode_1) run 10
  $_TMP(mode_1) setActiveSubGrids $_DM(1) [list]
  $_TMP(mode_1) run 100
  set _TMP(exam_1) [pw::Examine create "DomainLengthRatioJ"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  set _TMP(exam_2) [pw::Examine create "DomainLengthJ"]
  $_TMP(exam_2) addEntity [list $_DM(1)]
  $_TMP(exam_2) examine
  $_TMP(exam_2) delete
  unset _TMP(exam_2)
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  set _TMP(exam_1) [pw::Examine create "DomainSmoothnessI"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  set _TMP(exam_1) [pw::Examine create "DomainSmoothnessJ"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  set _TMP(exam_1) [pw::Examine create "DomainSkewEquiangle"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  set _TMP(exam_1) [pw::Examine create "DomainMinimumAngle"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  set _TMP(exam_1) [pw::Examine create "DomainMaximumAngle"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  pw::CutPlane applyMetric ""
  $_TMP(mode_1) setActiveSubGrids $_DM(1) [list]
  $_TMP(mode_1) run 100
  set _TMP(ENTS) [pw::Collection create]
$_TMP(ENTS) set [list $_DM(1)]
  $_DM(1) setEllipticSolverAttribute InteriorControl ThomasMiddlecoff
  $_TMP(ENTS) do setInitializeMethod Standard
  $_TMP(ENTS) delete
  unset _TMP(ENTS)
  set _TMP(exam_1) [pw::Examine create "DomainLengthRatioJ"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  set _TMP(exam_1) [pw::Examine create "DomainLengthJ"]
  $_TMP(exam_1) addEntity [list $_DM(1)]
  $_TMP(exam_1) examine
  pw::CutPlane applyMetric {}
  $_TMP(exam_1) delete
  unset _TMP(exam_1)
  pw::CutPlane applyMetric ""
  $_TMP(mode_1) setActiveSubGrids $_DM(1) [list]
  $_TMP(mode_1) run 100
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Solve}

set _TMP(mode_1) [pw::Application begin EllipticSolver [list $_DM(1)]]
$_TMP(mode_1) abort
unset _TMP(mode_1)
set _TMP(exam_1) [pw::Examine create "DomainLengthI"]
$_TMP(exam_1) addEntity [list $_DM(1)]
$_TMP(exam_1) examine
pw::CutPlane applyMetric {}
set _TMP(exam_2) [pw::Examine create "DomainLengthJ"]
$_TMP(exam_2) addEntity [list $_DM(1)]
$_TMP(exam_2) examine
$_TMP(exam_1) delete
unset _TMP(exam_1)
$_TMP(exam_2) delete
unset _TMP(exam_2)
set _TMP(exam_1) [pw::Examine create "DomainLengthJ"]
$_TMP(exam_1) addEntity [list $_DM(1)]
$_TMP(exam_1) examine
pw::CutPlane applyMetric {}
$_TMP(exam_1) delete
unset _TMP(exam_1)
pw::CutPlane applyMetric ""
pw::Display resetView -Z
set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(PW_1) [pw::FaceStructured createFromDomains [list $_DM(1)]]
  set _TMP(face_1) [lindex $_TMP(PW_1) 0]
  unset _TMP(PW_1)
  set _BL(1) [pw::BlockStructured create]
  $_BL(1) addFace $_TMP(face_1)
$_TMP(mode_1) end
unset _TMP(mode_1)
set _TMP(mode_1) [pw::Application begin ExtrusionSolver [list $_BL(1)]]
  $_TMP(mode_1) setKeepFailingStep true
  $_BL(1) setExtrusionSolverAttribute Mode Rotate
  $_BL(1) setExtrusionSolverAttribute RotateAxisStart {0 0 0}
  $_BL(1) setExtrusionSolverAttribute RotateAxisEnd [pwu::Vector3 add {0 0 0} {1 0 0}]
  $_BL(1) setExtrusionSolverAttribute RotateAngle 15
  $_TMP(mode_1) run 32
$_TMP(mode_1) end
unset _TMP(mode_1)
unset _TMP(face_1)
pw::Application markUndoLevel {Extrude, Rotate}

pw::Application save {/home/oliver/Repos/git/TestCases/hybrid/axibump/axibump_finer.pw}
pw::Application setCAESolver {SU2} 3
pw::Application markUndoLevel {Select Solver}

set _DM(2) [pw::GridEntity getByName dom-2]
set _DM(3) [pw::GridEntity getByName dom-3]
set _DM(4) [pw::GridEntity getByName dom-4]
set _DM(5) [pw::GridEntity getByName dom-5]
set _DM(6) [pw::GridEntity getByName dom-6]
set _TMP(PW_1) [pw::BoundaryCondition getByName Unspecified]
set _TMP(PW_2) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_3) [pw::BoundaryCondition getByName bc-2]
unset _TMP(PW_2)
$_TMP(PW_3) setName Inflow
pw::Application markUndoLevel {Name BC}

$_TMP(PW_3) apply [list [list $_BL(1) $_DM(5)]]
pw::Application markUndoLevel {Set BC}

set _TMP(PW_4) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_5) [pw::BoundaryCondition getByName bc-3]
unset _TMP(PW_4)
$_TMP(PW_5) apply [list [list $_BL(1) $_DM(3)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_5) setName Outflow
pw::Application markUndoLevel {Name BC}

set _TMP(PW_6) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_7) [pw::BoundaryCondition getByName bc-4]
unset _TMP(PW_6)
$_TMP(PW_7) apply [list [list $_BL(1) $_DM(4)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_7) setName Top
pw::Application markUndoLevel {Name BC}

set _TMP(PW_8) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_9) [pw::BoundaryCondition getByName bc-5]
unset _TMP(PW_8)
$_TMP(PW_9) apply [list [list $_BL(1) $_DM(2)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_9) setName Wall
pw::Application markUndoLevel {Name BC}

unset _TMP(PW_1)
unset _TMP(PW_3)
unset _TMP(PW_5)
unset _TMP(PW_7)
unset _TMP(PW_9)
set _TMP(PW_1) [pw::BoundaryCondition getByName Unspecified]
set _TMP(PW_2) [pw::BoundaryCondition getByName Inflow]
set _TMP(PW_3) [pw::BoundaryCondition getByName Outflow]
set _TMP(PW_4) [pw::BoundaryCondition getByName Top]
set _TMP(PW_5) [pw::BoundaryCondition getByName Wall]
pw::Display resetView -Z
set _TMP(PW_6) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_7) [pw::BoundaryCondition getByName bc-6]
unset _TMP(PW_6)
$_TMP(PW_7) setName Periodic0
pw::Application markUndoLevel {Name BC}

$_TMP(PW_7) apply [list [list $_BL(1) $_DM(1)]]
pw::Application markUndoLevel {Set BC}

set _TMP(PW_8) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_9) [pw::BoundaryCondition getByName bc-7]
unset _TMP(PW_8)
$_TMP(PW_9) apply [list [list $_BL(1) $_DM(6)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_9) setName Periodic1
pw::Application markUndoLevel {Name BC}

unset _TMP(PW_1)
unset _TMP(PW_2)
unset _TMP(PW_3)
unset _TMP(PW_4)
unset _TMP(PW_5)
unset _TMP(PW_7)
unset _TMP(PW_9)
pw::Application save {./axibump_512x256x33.pw}

