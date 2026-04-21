from EC_Admin.models import Candidates, Votes

election_id = 'test-1'
candidate_id = 'PC0018'

if Votes.objects.filter(election_id=election_id, candidate_id=candidate_id).exists():
    print('Votes record already exists')
else:
    try:
        c = Candidates.objects.get(candidate_id=candidate_id)
        constituency = c.parliamentary if c.parliamentary else c.assembly
        Votes.objects.create(
            election_id=election_id,
            candidate_id=candidate_id,
            candidate_name=c.name,
            candidate_party=c.candidate_party,
            state=c.state,
            constituency=constituency
        )
        print('Created Votes record')
    except Exception as e:
        print('Error:', e)
