error=0
for project in iouproject iou
do
  black $project || error=$?
  ruff check --fix --exit-non-zero-on-fix $project || error=$?
  isort --profile black $project || error=$?
done

# Make sure we don't have any translation updates
pushd iou && django-admin makemessages --locale en_US --locale fr && popd
django-admin compilemessages || error=$?
git diff --exit-code || error=$?

exit $error
