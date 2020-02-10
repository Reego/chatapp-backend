def simple_middleware(get_response):
    def middleware(request):
        # print('\n\nPROCESSING REQUEST\n')
        print(request.body)
        # for item in request.POST:
        #     print(item)
        # print('\nREQUEST PROCESSED\n\n')
        response = get_response(request)
        return response
    return middleware
