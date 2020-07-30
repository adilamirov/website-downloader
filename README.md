# Run

`docker-compose up`

# Use

## Create download task

`POST http://localhost:8080/tasks`

### Request example:

    {
        "url": "http://example.com/"
    }

### Response example:
    
    {
        "download_link": null,
        "id": "5f21d4b7661156e6f9418152",
        "status": "CREATED",
        "url": "http://example.com/"
    }

## Check task status

`GET http://localhost:8080/tasks/$id`

### Response example:

    {
        "download_link": "/upload/5f21d4b7661156e6f9418152.zip",
        "id": "5f21d4b7661156e6f9418152",
        "status": "COMPLETE",
        "url": "http://example.com/"
    }

## Download archive

`GET http://localhost:8080/upload/5f21d4b7661156e6f9418152.zip`
