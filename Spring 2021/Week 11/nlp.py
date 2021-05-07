from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import FinNews as fn

feed = fn.SeekingAlpha(topics=["$tsla"], save_feeds=True)

sa = pipeline('sentiment-analysis', model="ProsusAI/finbert", tokenizer="ProsusAI/finbert")


news = feed.get_news()
sent = {"positive":0, "neutral":0, "negative":0}
for i in news:
    print(i['title'])
    this_sent = sa(i['title'])
    print(this_sent)
    sent[this_sent[0]["label"]] += 1
    print("\n")
# print(len(news))
print(sent)
# print((sent['positive'])/len(news))
    

# while True:
#     print(sa(input(">> ")))

# tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")
# model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")

# # Let's chat for 5 lines
# for step in range(5):
#     # encode the new user input, add the eos_token and return a tensor in Pytorch
#     new_user_input_ids = tokenizer.encode(input(">> User:") + tokenizer.eos_token, return_tensors='pt')

#     # append the new user input tokens to the chat history
#     bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

#     # generated a response while limiting the total chat history to 1000 tokens, 
#     chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

#     # pretty print last ouput tokens from bot
#     print("DialoGPT: {}".format(tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)))