insert into roles (id, description) values ('admin','Administrator'),('agent','Support agent'),('customer','Customer') on conflict do nothing;
insert into knowledge_articles (title, body, tags) values ('Card dispute basics','We can help file a dispute. Never send a full card number in chat.', array['card','dispute']) on conflict do nothing;
