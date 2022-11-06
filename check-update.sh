#!/bin/sh
curl -s -L http://lame.sf.net 2>/dev/null |grep 'download.php">v' |sed -e 's,.*v,,;s,<.*,,'
