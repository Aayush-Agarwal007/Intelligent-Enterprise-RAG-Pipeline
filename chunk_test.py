from langchain_text_splitters import RecursiveCharacterTextSplitter
text="""
Employees are entitled to 18 days of annual leave per year.
Employees must submit their leave request through the employee portal.
Managers are responsible for approving or rejecting leave requests.
Unused annual leave may be carried forward according to company policy.
Employees should contact HR if they have questions about their leave balance.
"""
splitter=RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40
)
chunks=splitter.split_text(text)
print("total chunks:",len(chunks))
for i,chunk,in enumerate(chunks):
    print(f"\n--- Chunk{i+1} ---")
    print(chunk)