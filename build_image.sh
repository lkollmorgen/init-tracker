  #!/bin/sh

 docker build -t initiative-tracker .
 docker run --rm initiative-tracker pytest
