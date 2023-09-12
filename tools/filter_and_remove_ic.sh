# Script to remove images from a collection based on a time filter
# TODO: currently used with manual code commenting / editing, should become cli utility.

for img in `earthengine ls  projects/deltares-rws/eo-bathymetry/subtidal-nl \
--filter "\"system:time_start\" > 1675209600000"`; do
    earthengine rm $img
done