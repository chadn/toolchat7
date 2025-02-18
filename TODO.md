# To Do

-   :white_check_mark: Use Together AI instead of OpenAI
-   :white_check_mark: Enable save and restore by providing links to download and upload messages  
    BUG: must click download button twice to get latest json, can be fixed once "Deferred data" download button is released.
-   :white_check_mark: decouple chat model from functions.
-   :white_check_mark: create some pytest unit tests for functions, maybe for chat model
-   test using parea.ai
-   create a 100 examples of test chats

## Parea.ai

Temporary testing notes
https://docs.parea.ai/evaluation/overview
https://docs.parea.ai/welcome/getting-started-evaluation

```
python3 parea.eval.py
Run name set to: hilly-yegg, since a name was not provided.


Running samples: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 2584.29sample/s]
0it [00:04, ?it/s]
Experiment Greetings Run hilly-yegg stats:
{
  "latency": "0.00",
  "input_tokens": "0.00",
  "output_tokens": "0.00",
  "total_tokens": "0.00",
  "cost": "0.00000",
  "levenshtein": "0.78"
}


View experiment & traces at: https://app.parea.ai/experiments/Greetings/9f310edc-f2ea-4908-89fb-d999d4cb3f7f
```
