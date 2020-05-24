procedure TForm1.Button1Click(Sender:TObject);
begin
  try
    flag_correct := false;
    user_input := str_edit.GetText;
    user_input_length := Length(user_input);
    word_count := 1;
    tid_hash_msg_digest_5 := TIdHashMessageDigest5.Create;

    gvar_00458DFC := '1EFC99B6046A0F2C7E8C7EF9DC416323';
    gvar_00458E08 := '25DB3350B38953836C36DFB359DB4E27';
    gvar_00458E00 := 'C129BD7796F23B97DF994576448CAA23';
    gvar_00458E0C := '40A00CA65772D7D102BB03C3A83B1F91';
    gvar_00458E04 := '017EFBC5B1D3FB2D4BE8A431FA6D6258';

    if (user_input_length > 0)
        and (user_input[1] = 'C')
        and (user_input[2] = 'S')
        and (user_input[3] = 'C')
        and (user_input[4] = 'G')
        and (user_input[5] = '{')
        and (user_input[user_input_length] = '}') then
    begin
      for i := 1 to user_input_length do
        if user_input[i] = '_' then
          word_count += 1;
        end;
      end

      if word_count = 5 then
      begin

        flag_correct := true;
        user_input := AnsiMidStr(user_input, 6, user_input_length - 6);

        for i := 1 to word_count do
        begin
          underscore_pos := Pos('_', user_input);
          len := Length(user_input);
          if underscore_pos = 0 then
            underscore_pos := len + 1;
          end;
          curr_word := AnsiLeftStr(user_input, underscore_pos - 1);
          curr_word := AnsiReverseString(curr_word);
          hash_val := tid_hash_msg_digest_5.HashValue(curr_word);
          hash := tid_hash_msg_digest_5.AsHex(hash_val);

          if gvar_00458DF8[i] <> hash then
            flag_correct := false;
          end;

          user_input := AnsiRightStr(user_input, len - underscore_pos);
        end;
      end;
    end;

    if flag_correct then
      Application.MessageBox('That is the correct flag', 'Correnct');
      Exit;
    else
      Application.MessageBox('Looks like the wrong flag -.-', 'WRONG :P');
    end;

  finally
    user_input := '';
  end;
end;
