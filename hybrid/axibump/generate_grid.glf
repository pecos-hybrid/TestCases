# ---------------------------------------------------------------------
# Creates a hybrid RANS/LES mesh for the axisymmetric transonic bump
#
# For more details on the ATB case, see:
#     https://turbmodels.larc.nasa.gov/axibump_val.html
#
# To start with, you will need the `bump_newaxi_721.p2dfmt` grid from
# the NASA TMR website listed above. This will be used to initialize
# the mesh.
#
# Authors: T. Oliver, C. Pederson
# Compatible with: Pointwise V18.3
# ---------------------------------------------------------------------

package require PWI_Glyph 2.18.2

pw::Application setUndoMaximumLevels 5
pw::Application reset
pw::Application markUndoLevel {Journal Reset}

pw::Application clearModified

# ---------------------------------------------------------------------
# Script variables
# ---------------------------------------------------------------------

# All dimensions are normalized by c, the bump length

# ---------------------------------------------------------------------
# Azimuthal spacing
# ---------------------------------------------------------------------
# Number of grid points in each direction
set Ntheta 3
# Azimuthal extent of the domain, in degrees
set azimuthal_angle 1

# ---------------------------------------------------------------------
# Streamwise spacing
# ---------------------------------------------------------------------
# Spacing at the inlet
set inlet_delta_x 0.05
# Spacing at the outlet
set outlet_delta_x 0.10
# Spacing near x/c = -1
set approach_delta_x 0.009
# Spacing near x/c = 0.5
set crest_delta_x 0.002
# Spacing near separation
set separation_delta_x 0.002
# Spacing at x/c = 1
set bump_end_delta_x 0.002

# ---------------------------------------------------------------------
# Wall-normal spacing
# ---------------------------------------------------------------------
# Wall-normal spacing, at y+ \approx 100, x/c = -1
set approach_delta_r 1.6E-4
# Wall-normal spacing, at the wall, at inlet
set inlet_delta_r 5.0e-06
# Wall-normal spacing, at the wall, at the outlet
set outlet_delta_r 5.0e-06
# Wall-normal spacing, at the edge of the boundary layer
# Boundary layer thickness is about 0.032 c at x/c = -1
set delta_r_BL_edge 1.6e-3
# Wall-normal spacing, at the top
set top_delta_r 0.10

# Input basic grid
set p2d_file {/home/clark/Downloads/axibump/grids/bump_newaxi_721.p2dfmt}
# Output Pointwise project file
set pw_file {/home/clark/Downloads/axibump/grids/axibump_very_coarse_narrow.pw}
# Output su2 file
set su2_file /home/clark/Downloads/axibump/grids/axibump_very_coarse_narrow.su2
# Output cgns file
set cgns_file /home/clark/Downloads/axibump/grids/axibump_very_coarse_narrow.cgns

# ---------------------------------------------------------------------
# Script variables
# ---------------------------------------------------------------------

set _TMP(mode_1) [pw::Application begin GridImport]
  $_TMP(mode_1) initialize -strict -type {PLOT3D} $p2d_file
  $_TMP(mode_1) read
  $_TMP(mode_1) convert
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Import Grid}

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

set con1 [pw::GridEntity getByName con-1]
set con2 [pw::GridEntity getByName con-2]
set con3 [pw::GridEntity getByName con-3]
set con4 [pw::GridEntity getByName con-4]

set _TMP(mode_1) [pw::Application begin Modify [list $con1 $con3]]
  $con1 addBreakPoint -arc 0.484506213477
  $con1 addBreakPoint -X 0.69899664
  $con1 addBreakPoint -X 1.0023381
  [[$con1 getDistribution 1] getBeginSpacing] setValue $inlet_delta_x
  [[$con1 getDistribution 1] getEndSpacing] setValue $crest_delta_x
  [[$con1 getDistribution 2] getBeginSpacing] setValue $crest_delta_x
  [[$con1 getDistribution 2] getEndSpacing] setValue $separation_delta_x
  [[$con1 getDistribution 3] getBeginSpacing] setValue $separation_delta_x
  [[$con1 getDistribution 3] getEndSpacing] setValue $bump_end_delta_x
  [[$con1 getDistribution 4] getBeginSpacing] setValue $bump_end_delta_x
  [[$con1 getDistribution 4] getEndSpacing] setValue $outlet_delta_x
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

# ---------------------------------------------------------------------
# Add in spacing constraints for x/c = -1
# ---------------------------------------------------------------------

set _TMP(mode_1) [pw::Application begin Modify [list $con1]]
  $con1 addBreakPoint -X -1
  [[$con1 getDistribution 2] getBeginSpacing] setValue $approach_delta_x
  [[$con1 getDistribution 1] getEndSpacing] setValue $approach_delta_x
  $con1 setSubConnectorDimensionFromDistribution 2
  $con1 setSubConnectorDimensionFromDistribution 5
  $con1 setSubConnectorDimensionFromDistribution 4
  $con1 setSubConnectorDimensionFromDistribution 3
  $con1 setSubConnectorDimensionFromDistribution 1
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

# Fixed???
set Nx [$con1 getDimension]
$con3 setDimension $Nx
pw::CutPlane refresh
pw::Application markUndoLevel {Dimension}

set _TMP(mode_1) [pw::Application begin Modify [list $con3]]
  set _CN(2) [pw::GridEntity getByName con-1]
  set _TMP(dist_1) [pw::DistributionGeneral create [list [list $_CN(2) 5] [list $_CN(2) 4] [list $_CN(2) 3] [list $_CN(2) 2] [list $_CN(2) 1]]]
  # Clear spacings so the distribution will scale properly
  $_TMP(dist_1) setBeginSpacing 0
  $_TMP(dist_1) setEndSpacing 0
  $_TMP(dist_1) setVariable [[$con3 getDistribution 1] getVariable]
  $con3 setDistribution -lockEnds 1 $_TMP(dist_1)
  unset _TMP(dist_1)
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

# ---------------------------------------------------------------------
# Setup the inlet spacing
# ---------------------------------------------------------------------

set _TMP(mode_1) [pw::Application begin Modify [list $con4]]
  $con4 addBreakPoint -Y 0.376
  [[$con4 getDistribution 1] getBeginSpacing] setValue $top_delta_r
  [[$con4 getDistribution 2] getEndSpacing] setValue $inlet_delta_r
  [[$con4 getDistribution 2] getBeginSpacing] setValue $approach_delta_r
  [[$con4 getDistribution 1] getEndSpacing] setValue $approach_delta_r
  $con4 setSubConnectorDimensionFromDistribution 1
  $con4 setSubConnectorDimensionFromDistribution 2
  $con4 addBreakPoint -Y 0.425
  [[$con4 getDistribution 2] getBeginSpacing] setValue $delta_r_BL_edge
  [[$con4 getDistribution 1] getEndSpacing] setValue $delta_r_BL_edge
  $con4 setSubConnectorDimensionFromDistribution 1
  $con4 setSubConnectorDimensionFromDistribution 2
  $con4 setSubConnectorDimensionFromDistribution 3
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

# Fixed???
set Nr [$con4 getDimension]
$con2 setDimension $Nr
pw::CutPlane refresh
pw::Application markUndoLevel {Dimension}

# ---------------------------------------------------------------------
# Outlet wall-normal spacing
# ---------------------------------------------------------------------

set _TMP(mode_1) [pw::Application begin Modify [list $con2]]
  [[$con2 getDistribution 1] getBeginSpacing] setValue $outlet_delta_r
  [[$con2 getDistribution 1] getEndSpacing] setValue $top_delta_r
  $con2 replaceDistribution 1 [pw::DistributionTanh create]
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Distribute}

set _DM(1) [pw::GridEntity getByName dom-1]
set _TMP(mode_1) [pw::Application begin EllipticSolver [list $_DM(1)]]
  $_TMP(mode_1) run 55
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Solve}

# ---------------------------------------------------------------------
# Extrude in azimuthal direction
# ---------------------------------------------------------------------

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
  $_BL(1) setExtrusionSolverAttribute RotateAngle $azimuthal_angle
  $_TMP(mode_1) run [expr {$Ntheta-1}]
$_TMP(mode_1) end
unset _TMP(mode_1)
unset _TMP(face_1)
pw::Application markUndoLevel {Extrude, Rotate}

# ---------------------------------------------------------------------
# BCs
# ---------------------------------------------------------------------

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

# ---------------------------------------------------------------------
# Save pointwise
# ---------------------------------------------------------------------
#
pw::Application save $pw_file

# ---------------------------------------------------------------------
# Export su2 file
# ---------------------------------------------------------------------

set _TMP(mode_1) [pw::Application begin CaeExport]
  $_TMP(mode_1) addAllEntities
  $_TMP(mode_1) initialize -strict -type CAE $su2_file
  $_TMP(mode_1) setAttribute FilePrecision Double
  $_TMP(mode_1) verify
  $_TMP(mode_1) write
$_TMP(mode_1) end
unset _TMP(mode_1)

# ---------------------------------------------------------------------
# Also save to CGNS to preserve structured data
# ---------------------------------------------------------------------

pw::Application setCAESolver {CGNS} 3
pw::Application markUndoLevel {Select Solver}

set _TMP(mode_1) [pw::Application begin CaeExport]
  $_TMP(mode_1) addAllEntities
  $_TMP(mode_1) initialize -strict -type CAE $cgns_file
  $_TMP(mode_1) setAttribute FilePrecision Double
  $_TMP(mode_1) setAttribute ExportDonorInformation false
  $_TMP(mode_1) verify
  $_TMP(mode_1) write
$_TMP(mode_1) end
unset _TMP(mode_1)
