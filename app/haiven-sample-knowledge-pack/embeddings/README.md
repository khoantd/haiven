
These are sample knowledge bases that can be questioned in the "Knowledge Chat" tab of the Haiven UI, and also pulled into chat conversations as additional resources.

For this to work in the application, you need to run Haiven with access to the embeddings model that created these, so that the user's questions can be matched. The markdown files mention the "provider" used to create the embeddings, you'll find the corresponding embeddings model in [Haiven's `config.yaml`](https://github.com/tw-haiven/haiven/blob/main/app/config.yaml).

Note that the Retrieval-Augmented Generation (RAG) implementation in Haiven is VERY basic, as everything happens in memory only. We currently prioritise simple deployment over sophisticated RAG. We want it to be "just good enough" to give experimenters an indication of the potential. If you like the Haiven sandbox as a starting point, but would like more powerful RAG capabilities, you would have to change the [Haiven code](https://github.com/tw-haiven) to connect to a proper information retrieval setup, like e.g. one of the big cloud providers' AI studios. 

# Make request to create index
    ```
    curl -X POST "http://localhost:8080/api/embeddings" \                                     
    -H "Content-Type: application/json" \
    -d '{
        "text": "This is the Technology Radar document",
        "metadata": {
        "key": "tr-technology-radar-vol-31",
        "title": "Technology Radar Vol 31",
        "description": "Thoughtworks Technology Radar Volume 31",
        "source": "tr_technology_radar_vol_31_en.pdf",
        "path": "tr_technology_radar_vol_31_en.pdf",
        "provider": "openai",
        "context": "base"
        },
        "output_path": "haiven-sample-knowledge-pack/embeddings/blips_vol_31_openai.kb"
    }'
    ```
  # Create folder
  ```
  mkdir blips_vol_31_openai.kb
  ```
  # create metadata file
  ```
    ---
    key: radar-vol-31_openai
    title: Technology Radar Vol 31
    description: Thoughtworks Technology Radar, volume 31
    source: tr_technology_radar_vol_31_en.pdf
    path: blips_vol_31_openai.kb
    provider: openai
    sample_question: "I build a lot of Microservices, what's interesting for me?"
    ---
  ```