error=0
for project in iouproject iou
do
  black $project || error=$?
  ruff check --fix --exit-non-zero-on-fix $project || error=$?
  isort --profile black $project || error=$?
done
exit $error
