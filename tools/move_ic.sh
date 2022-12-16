for img in `earthengine ls "projects/deltares-rws/eo-bathymetry/depth-uncalibrated-nl"`; do
	earthengine mv $img "projects/deltares-rws/eo-bathymetry/subtidal-nl/${img##*/}"
done
