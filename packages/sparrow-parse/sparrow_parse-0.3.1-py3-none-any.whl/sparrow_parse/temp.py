# content, table_content = processor.extract_data(
    #     '/Users/andrejb/Documents/work/schreiber/invoice_data/test/2618407.pdf',
    #     'hi_res',
    #     'yolox',
    #     # 'detectron2_onnx',
    #     ['tables', 'unstructured'],
    #     True,
    #     True)

    # content, table_content = processor.extract_data(
    #     '/Users/andrejb/Documents/work/epik/bankstatement/OCBC_1_1.pdf',
    #     'hi_res',
    #     'yolox',
    #     ['tables', 'unstructured'],
    #     True,
    #     True)

    # output_directory = "/Users/andrejb/Documents/work/epik/bankstatement/output_pages"
    # # Ensure the output directory exists
    # os.makedirs(output_directory, exist_ok=True)
    #
    # # Split the optimized PDF into separate pages
    # num_pages, output_files, temp_dir = pdf_optimizer.split_pdf_to_pages("/Users/andrejb/Documents/work/epik/bankstatement/OCBC_1_statement.pdf",
    #                                                                      output_directory,
    #                                                                      False)
    #
    # shutil.rmtree(temp_dir, ignore_errors=True)