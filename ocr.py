import replicate
from ocrmac import ocrmac
from scipy.spatial.distance import cosine
import numpy as np
from recorder import screenshot
import json
import time
from pydantic import BaseModel
from datetime import datetime

PRODUCTIVITY_WORDS = ["social media", "distracting"]
PRODUCTIVITY_THRESHOLD = .78


deployment = replicate.deployments.get("cbh123/coach-embedder")
productivity_prediction = deployment.predictions.create(
    input={
        "texts": json.dumps(PRODUCTIVITY_WORDS),
    }
)
productivity_prediction.wait()
productivity_embedding = np.array(productivity_prediction.output)

class EmbeddingLog(BaseModel):
    datetime: datetime
    image_path: str
    aggregate_distance: float
    model: str = "nateraw/bge-large-en-v1.5"
    iteration_duration: float
    replicate_prediction: str
    is_productive: bool = None

while True:
    start = time.time()
    path = screenshot()
    annotations = ocrmac.OCR(path).recognize()

    # Extract the first element of each tuple and format it into the desired string format
    formatted_strings = [f'"{item[0]}"' for item in annotations if item[1] == 1.0]

    print(f"Formatted strings: {json.dumps(formatted_strings)}")
    screen_prediction = deployment.predictions.create(
       input={"texts": json.dumps(formatted_strings)}
    )

    screen_prediction.wait()
    screen_embedding = np.array(screen_prediction.output)

    import numpy as np
    from scipy.spatial.distance import cosine

    # Calculate the mean of each set of embeddings
    mean_screen_embedding = np.mean(screen_embedding, axis=0)
    mean_productivity_embedding = np.mean(productivity_embedding, axis=0)

    # Calculate the cosine similarity between the mean embeddings
    aggregate_distance = 1 - cosine(mean_screen_embedding, mean_productivity_embedding)

    print("SCORE: ", aggregate_distance)
    if aggregate_distance > PRODUCTIVITY_THRESHOLD:
        print("NOT PRODUCTIVE")
        from utils import send_notification
        send_notification("Not productive!", "Score is: " + str(aggregate_distance))

    end = time.time()
    print(f"Time taken: {end - start:.2f}s")

    emebedding_log = EmbeddingLog(
        datetime=datetime.now(),
        image_path=path,
        replicate_prediction=screen_prediction.id,
        aggregate_distance=aggregate_distance,
        iteration_duration=end - start
    )

    # save the activity to a file
    with open("./logs/embeddings.jsonl", "a") as f:
        f.write(emebedding_log.model_dump_json() + "\n")
    time.sleep(1)
