#!/bin/bash
rm -r */
git clone https://github.com/SWE-AGGERS/api_gateway.git --single-branch --branch master
git clone https://github.com/SWE-AGGERS/users_service.git  --single-branch --branch master
git clone https://github.com/SWE-AGGERS/background-service.git --single-branch --branch master 
git clone https://github.com/SWE-AGGERS/socialdice_profiling.git --single-branch --branch dockerize 
git clone https://github.com/SWE-AGGERS/DiceManagement.git --single-branch --branch master 
git clone https://github.com/SWE-AGGERS/stories_service.git --single-branch --branch master 
git clone https://github.com/SWE-AGGERS/reactions_service.git --single-branch --branch master 
git clone https://github.com/SWE-AGGERS/search_service.git --single-branch --branch master 
rm background-service/docker-compose.yml
rm DiceManagement/docker-compose.yml
rm reactions_service/docker-compose.yml
rm search_service/docker-compose.yml
rm socialdice_profiling/docker-compose.yml
rm stories_service/docker-compose.yml
