import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DialogShowEditTask } from './dialog-show-edit-task';

describe('DialogShowEditTask', () => {
  let component: DialogShowEditTask;
  let fixture: ComponentFixture<DialogShowEditTask>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DialogShowEditTask]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DialogShowEditTask);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
