#include <string>

#include "server_seg_api.h"

int main(int argc, char* argv[]) {
  int port = 9090;
  int thread_num = 8;
  std::string model_path =
      "/mnt/c/Users/luc/Desktop/liangbo/projects/api_seg/models_general/lac_model";
  std::string custom_dict_path =
      "/mnt/c/Users/luc/Desktop/liangbo/projects/api_seg/custom_dict.txt";
  if (argc >= 4) {
    port = atoi(argv[1]);
    thread_num = atoi(argv[2]);
    model_path = argv[3];
    custom_dict_path = argv[4];
  }

  ServerSegApi server(port, thread_num, model_path, custom_dict_path);
  server.Run();

  return 0;
}
