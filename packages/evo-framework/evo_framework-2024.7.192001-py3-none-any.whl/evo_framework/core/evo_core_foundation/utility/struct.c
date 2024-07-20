struct EPack {
    bool isChunk;
    char[32] id; //32 length
    long offsetStart;
    long offsetEnd;
    long dataLength;
};