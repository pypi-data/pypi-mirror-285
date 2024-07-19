#!/usr/bin/env bash

python -m grpc_tools.protoc -I../../backend/proto  -I../../backend/proto/google/api --python_out=src/xai_sdk/proto --pyi_out=src/xai_sdk/proto --grpc_python_out=src/xai_sdk/proto ../../backend/proto/chat.proto ../../backend/proto/prod_search.proto ../../backend/proto/sampler_public.proto ../../backend/proto/google/api/annotations.proto ../../backend/proto/google/api/http.proto ../../backend/proto/files.proto ../../backend/proto/stateless_chat.proto ../../backend/proto/x_entities.proto ../../backend/proto/compat_chat.proto ../../backend/proto/embedder_public.proto
python -m grpc_tools.protoc -I../../../prod/ic/inference-api/proto-public --python_out=src/xai_sdk/proto/v2 --pyi_out=src/xai_sdk/proto/v2 --grpc_python_out=src/xai_sdk/proto/v2 ../../../prod/ic/inference-api/proto-public/chat.proto ../../../prod/ic/inference-api/proto-public/embed.proto ../../../prod/ic/inference-api/proto-public/image.proto ../../../prod/ic/inference-api/proto-public/models.proto

# Change imports to be relative
for file in src/xai_sdk/proto/*; do
  # Check if the file is a regular file
  if [[ -f "$file" ]]; then
    sed -i '' 's/^import chat_pb2/from . import chat_pb2/' "$file"
    sed -i '' 's/^import compat_chat_pb2/from . import compat_chat_pb2/' "$file"
    sed -i '' 's/^import embedder_public_pb2/from . import embedder_public_pb2/' "$file"
    sed -i '' 's/^import files_pb2/from . import files_pb2/' "$file"
    sed -i '' 's/^import prod_search_pb2/from . import prod_search_pb2/' "$file"
    sed -i '' 's/^import sampler_public_pb2/from . import sampler_public_pb2/' "$file"
    sed -i '' 's/^import stateless_chat_pb2/from . import stateless_chat_pb2/' "$file"
    sed -i '' 's/^import x_entities/from . import x_entities/' "$file"
    sed -i '' 's/^from google.api/from .google.api/' "$file"
  fi
done

# Change imports to be relative
for file in src/xai_sdk/proto/v2/*; do
  # Check if the file is a regular file
  if [[ -f "$file" ]]; then
    sed -i '' 's/^import chat_pb2/from . import chat_pb2/' "$file"
    sed -i '' 's/^import embed_pb2/from . import embed_pb2/' "$file"
    sed -i '' 's/^import models_pb2/from . import models_pb2/' "$file"
    sed -i '' 's/^import image_pb2/from . import image_pb2/' "$file"
  fi
done


for file in src/xai_sdk/proto/google/api/*; do
  if [[ -f "$file" ]]; then
    sed -i '' 's/^from google.api import/from . import/' "$file"
  fi
done

# Recursively find all Python files in a directory and insert the comment "fmt: off" at the top of
# every file.Without this, the presubmit check makes noise.
find ./src/xai_sdk/proto -type f -name "*.py" -not -path "*/__init__.py" | while read file; do
    # Insert the comment at the top of the file
    echo "# fmt: off" | cat - "$file" > temp && mv temp "$file"
done

find ./src/xai_sdk/proto/v2 -type f -name "*.py" -not -path "*/__init__.py" | while read file; do
    # Insert the comment at the top of the file
    echo "# fmt: off" | cat - "$file" > temp && mv temp "$file"
done