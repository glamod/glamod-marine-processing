
pyEnvironment_directory=$home_directory/obs-suite/pyenvs/envichec
# Activate python environment and add jaspy3.7 path to LD_LIBRARY_PATH so that cartopy and other can find the geos library
source activate $pyEnvironment_directory
export PYTHONPATH="$pyTools_directory:${PYTHONPATH}"
#export LD_LIBRARY_PATH=/apps/contrib/jaspy/miniconda_envs/jaspy3.7/m3-4.5.11/envs/jaspy3.7-m3-4.5.11-r20181219/lib/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/ichec/packages/conda/2/lib/:$LD_LIBRARY_PATH

echo "Python environment loaded from gws: $pyEnvironment_directory"
