@echo off
setlocal
set CONTAINER_NAME=oai2ollama
set IMAGE_NAME=oai2ollama
set OPENAI_API_KEY=example_key
set OPENAI_BASE_URL=https://api-inference.modelscope.cn/v1/

docker rm -f %CONTAINER_NAME% >nul 2>nul

docker run -it --name %CONTAINER_NAME% ^
  -p 11434:11434 ^
  %IMAGE_NAME% ^
  --api-key "%OPENAI_API_KEY%" ^
  --base-url "%OPENAI_BASE_URL%" %*

endlocal
pause