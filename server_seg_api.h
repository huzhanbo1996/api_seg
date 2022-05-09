#pragma once
#include <mutex>
#include <sstream>
#include <string>
#include <vector>

#include "lac.h"
#include "workflow/HttpMessage.h"
#include "workflow/HttpUtil.h"
#include "workflow/WFFacilities.h"
#include "workflow/WFHttpServer.h"
#include "workflow/WFServer.h"

class ServerSegApi {
 private:
  static WFFacilities::WaitGroup global_wait_group_;
  static void StopWaitGroup(int signal);

  void Process(WFHttpTask* server_task);
  void SegText(std::istringstream& query_text,
               std::ostringstream& response_text);

  int port_;
  int thread_num_;
  LAC lac_model_;

  std::mutex lock_response_text_;
  std::mutex lock_query_text_;

 public:
  void Run();
  ServerSegApi(int port, int thread_num, const std::string& model_path,
               const std::string& custom_dict_path)
      : port_(port), thread_num_(thread_num), lac_model_(model_path) {
    lac_model_.load_customization(custom_dict_path);
  }
  ~ServerSegApi() {}
};
