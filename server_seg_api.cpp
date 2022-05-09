#include "server_seg_api.h"

#include <signal.h>

#include "rapidjson/document.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"

WFFacilities::WaitGroup ServerSegApi::global_wait_group_(1);

void ServerSegApi::Run() {
  signal(SIGINT, &StopWaitGroup);

  WFHttpServer server(
      std::bind(&ServerSegApi::Process, this, std::placeholders::_1));

  if (server.start(port_) == 0) {
    global_wait_group_.wait();
    server.stop();
  } else {
    perror("Cannot start server");
    exit(1);
  }
}

void ServerSegApi::StopWaitGroup(int signal) { global_wait_group_.done(); }

// TODO: Too large line will crash the model, make sure not happen
void ServerSegApi::SegText(std::istringstream &query_text,
                           std::ostringstream &response_text) {
  LAC local_model(lac_model_);
  std::string line;

  while (true) {
    lock_query_text_.lock();
    if (query_text.eof()) {
      lock_query_text_.unlock();
      break;
    } else {
      std::string tmp;
      std::getline(query_text, tmp);
      line = std::string(tmp.c_str());
    }
    lock_query_text_.unlock();

    std::ostringstream curr_line_seg_;
    if (!line.empty()) {
      const auto &result = local_model.run(line);
      for (size_t i = 0; i < result.size(); i++) {
        if (result[i].tag.length() == 0) {
          curr_line_seg_ << result[i].word << " ";
        } else {
          curr_line_seg_ << result[i].word << "/" << result[i].tag << " ";
        }
      }
    } else {
      curr_line_seg_ << "";
    }

    lock_response_text_.lock();
    response_text << curr_line_seg_.str();
    lock_response_text_.unlock();
  }
}

void ServerSegApi::Process(WFHttpTask *server_task) {
  protocol::HttpRequest *req = server_task->get_req();
  protocol::HttpResponse *resp = server_task->get_resp();
  std::ostringstream response_text;
  std::istringstream query_text;
  long long seq = server_task->get_task_seq();
  const void *body;
  size_t body_len;
  req->get_parsed_body(&body, &body_len);

  // make input text to stream
  query_text = std::istringstream(std::string((const char *)body, body_len));

  // seg text
  std::vector<std::thread> threads;
  for (int i = 0; i < thread_num_; i++) {
    std::thread th(&ServerSegApi::SegText, this, std::ref(query_text),
                   std::ref(response_text));
    threads.push_back(move(th));
  }

  for (auto &th : threads) {
    if (th.joinable()) {
      th.join();
    }
  }

  // append output to body
  resp->append_output_body(response_text.str());

  // make header
  resp->set_http_version("HTTP/1.1");
  resp->set_status_code("200");
  resp->set_reason_phrase("OK");
  resp->add_header_pair("Content-Type", "text/html");
  resp->add_header_pair("Server", "Luc's server");

  // no more than 10 requests on the same connection
  if (seq == 9) resp->add_header_pair("Connection", "close");
}
