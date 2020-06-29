from mp4struct import BitArray


UseDefaultScalingMatrix4x4Flag = [16 for i in range(16)]
UseDefaultScalingMatrix8x8Flag = [16 for i in range(64)]

def sps_test(data):
    bitarray = BitArray(data)
    nal_type = bitarray.read_bit(8)
    profile_idc = bitarray.read_bit(8)
    constraint_set0_flag = bitarray.read_bit()
    constraint_set1_flag = bitarray.read_bit()
    constraint_set2_flag = bitarray.read_bit()
    constraint_set3_flag = bitarray.read_bit()
    constraint_set4_flag = bitarray.read_bit()
    constraint_set5_flag = bitarray.read_bit()
    reserved_zero_2bits = bitarray.read_bit(2)
    level_idc = bitarray.read_bit(8)
    seq_parameter_set_id = bitarray.get_ue()
    if profile_idc in [100, 110, 122, 244, 44, 83, 86, 118, 128, 138, 139, 134, 135]:
        chroma_format_idc = bitarray.get_ue()
        # print(chroma_format_idc)
        if chroma_format_idc == 3:
            separate_colour_plane_flag = bitarray.read_bit()
        bit_depth_luma_minus8 = bitarray.get_ue()
        bit_depth_chroma_minus8 = bitarray.get_ue()
        qpprime_y_zero_transform_bypass_flag = bitarray.read_bit()
        seq_scaling_matrix_present_flag = bitarray.read_bit()
        if seq_scaling_matrix_present_flag:
            if chroma_format_idc != 3:
                index = 8
            else:
                index = 12
            seq_scaling_list_present_flag = [None] * index
            for i in range(index):
                seq_scaling_list_present_flag[i] = bitarray.read_bit()
                if seq_scaling_list_present_flag[i]:
                    if i < 6:
                        scaling_list(ScalingList4x4[i], 16, UseDefaultScalingMatrix4x4Flag[i])
                    else:
                        scaling_list(ScalingList8x8[i - 6], 64, UseDefaultScalingMatrix8x8Flag[i - 6])

        log2_max_frame_num_minus4 = bitarray.get_ue()
        pic_order_cnt_type = bitarray.get_ue()
        if pic_order_cnt_type == 0:
            log2_max_pic_order_cnt_lsb_minus4 = bitarray.get_ue()
        elif pic_order_cnt_type == 1:
            delta_pic_order_always_zero_flag = bitarray.read_bit()
            offset_for_non_ref_pic = bitarray.get_se()
            offset_for_top_to_bottom_field = bitarray.get_se()
            num_ref_frames_in_pic_order_cnt_cycle = bitarray.get_ue()
            for i in range(num_ref_frames_in_pic_order_cnt_cycle):
                bitarray.get_se()
        max_num_ref_frames = bitarray.get_ue()
        gaps_in_frame_num_value_allowed_flag = bitarray.read_bit()
        pic_width_in_mbs_minus1 = bitarray.get_ue()
        pic_height_in_map_units_minus1 = bitarray.get_ue()
        print(pic_width_in_mbs_minus1, pic_height_in_map_units_minus1)
        frame_mbs_only_flag = bitarray.read_bit()
        if not frame_mbs_only_flag:
            mb_adaptive_frame_field_flag = bitarray.read_bit()
        direct_8x8_inference_flag = bitarray.read_bit()
        frame_cropping_flag = bitarray.read_bit()
        if frame_cropping_flag:
            frame_crop_left_offset = bitarray.get_ue()
            frame_crop_right_offset = bitarray.get_ue()
            frame_crop_right_offset = bitarray.get_ue()
            frame_crop_right_offset = bitarray.get_ue()
        vui_parameters_present_flag = bitarray.read_bit()

def scaling_list(scalingList, sizeOfScalingList, useDefaultScalingMatrixFlag):
    lastScale = 8
    nextScale = 8
    for j in range(sizeOfScalingList):
        if nextScale != 0:
            delta_scale = bitarray.get_se()
            nextScale = ( lastScale + delta_scale + 256 ) % 256
            useDefaultScalingMatrixFlag = ( j == 0 and nextScale == 0 )
        if nextScale == 0:
            scalingList[j] = lastScale
        else:
            scalingList[j] = nextScale





sps = b'\x67\x64\x00\x28\xAC\x3B\x50\x3C\x01\x13\xF2\xC2\x00\x00\x03\x00\x02\x00\x00\x03\x00\x3D\x08'   # t21_sps_info
# sps = b'\x27\x64\x00\x33\xAD\x00\xCE\x80\x24\x00\xA3\xA6\xA0\x20\x20\x3E\x00\x00\x03\x00\x02\x00\x00\x03\x00\x64\x71\x40\x7D\x00\xBB\xBF\xFF\x81\x40'   # t31_264_sps
sps_test(sps)
