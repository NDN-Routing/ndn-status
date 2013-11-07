<?php

echo shell_exec("ssh ndnmonitor@netlogic.cs.memphis.edu pgrep ospfn || echo Down");

?>

