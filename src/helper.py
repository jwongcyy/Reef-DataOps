import io


# This method for inserting row record to the data sheet on AWS S3
def post_record(new_record, source_df, store_obj, output_path, df_id=None):
    record_added = False
    records_num = source_df.shape[0]
    if df_id:
        # update the new record id
        record_id = source_df.iloc[-1][df_id] + 1
        # update last row with new
        # source_df = source_df._append(new_record, ignore_index=True)
        # update last row inplace (by refrence)
        source_df.loc[len(source_df)] = new_record
        source_df.loc[source_df.index[-1], df_id] = record_id
        source_df[df_id] = source_df[df_id].astype('int')
    else:
        source_df.loc[len(source_df)] = new_record
    if source_df.shape[0] > records_num:
        record_added = True
    if record_added:
        csv_buffer = io.StringIO()
        source_df.to_csv(csv_buffer, index=False)
        post_result = store_obj.write_file(binary_data=csv_buffer.getvalue(),
                                           output_path=output_path)
        if post_result['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
    return False
