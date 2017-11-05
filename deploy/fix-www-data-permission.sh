find . -name *.db -exec chown www-data:www-data {} \;
find . -name *.db -exec chmod 777 {} \;
find . -name db -type d -exec chown www-data:www-data {} \; 
find . -name uploads -type d -exec chown www-data:www-data {} \; 