echo "You have installed test-package!"
echo "You need to enter path for unit-testing"
echo "Please refer to exist directory of source!"
read -p "Dirname: " source_path
command -v pytest >> /dev/null || (echo "You haven't installed pytest, abort!"; exit 1)
( cd $source_path || echo "Path not exists, abort"; exit 2 ) && pytest
