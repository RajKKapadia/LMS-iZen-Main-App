* Stop the existing container
    ```bash
    docker ps
    ```
    Get the id of the existing running container then,
    
    ```bash
    docker stop container_id
    ```
* Build the image
    ```bash
    docker build -t chat-widget .
    ```
* Run the docker image
    ```bash
    docker run -p 3000:3000 --netwrok host --restart unless-stopped chat-widget
    ```