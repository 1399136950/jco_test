int BM(const string &str, const string &pat)
{
    //定义并构造bm_map
    unordered_map<char, int> bm_map;
    for (int k = 0; k < pat.size(); ++k)
    {
        bm_map[pat[i]] = i;
    }

    //BM算法主体
    int i = 0, j = 0;
    unordered_map<char, int>::const_iterator ite;
    while (i <= str.size() - pat.size())
    {
        for (j = pat.size()-1; j >= 0; --j)
        {
            if (pat[j] != str[i+j])
            {
                if (bm_map.cend() != (ite = bm_map.find(str[i+j])))
                {
                    i += j - ite->second;
                }
                else
                {
                    i += j+1;
                }
                break;
            }
        }
        if (j < 0)
        {
            return i;
        }
    }
    return -1;
} 
